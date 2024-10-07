import pandas as pd
import numpy as np
import camelot
import time
import os

# Add timestamp right at the end of the filename when exporting to CSV.
# This is to skip file check permission when replacing the file.
time_str = time.strftime("%Y%m%d_%H%M%S")

# Detect platform and set file paths accordingly
PDF_LINK = os.path.join('data', 'tng_ewallet_transactions.pdf')
CSV_LINK = os.path.join('output', f'tng_ewallet_transactions_{time_str}.csv')

# Read PDF Statement into a table collection, the areas/regions and columns separators is self-defined
table = camelot.read_pdf(PDF_LINK, pages='all', flavor='stream',
    table_regions=['20,600,820,50'], table_areas=['20,600,820,50'], 
    columns=['80,140,230,294,460,660,720'], 
    split_text=True, strip_text='\n')

# Merge all tables and clean the data
df = (
    pd
    .concat([tbl.df for tbl in table._tables], ignore_index=True)
    .set_axis(['Date', 'Status', 'Transaction Type', 'Reference', 'Description', 'Details', 'Amount (RM)', 'Wallet Balance'], axis=1)
    .query(r'Date.str.contains(r"^\d|^$", na=True) & ~Reference.str.contains(r"^$")', engine='python')
    .assign(idx=lambda x: (~x.Date.str.contains('^$')).cumsum())
    .groupby('idx')
    .apply(lambda x: x.apply(lambda y: ' '.join(y.fillna('').astype(str))).str.strip())
    .reset_index(drop=True)
    .drop(['idx', 'Status', 'Reference', 'Details'], axis=1)
    .assign(
        Date=lambda x: pd.to_datetime(x.Date, format=r'%d/%m/%Y'),
        **{
            'Amount (RM)': lambda x: x['Amount (RM)'].str.replace(r'[^\d.]', '', regex=True).astype(float),
            'Wallet Balance': lambda x: x['Wallet Balance'].str.replace(r'[^\d.]', '', regex=True).astype(float)
        }
    )
)

# Separate the transactions with normal trx (df1) and GO+ trx (df2)
df1 = df.loc[lambda x: ~x['Transaction Type'].str.startswith('GO+')]
df2 = df.loc[lambda x: x['Transaction Type'].str.startswith('GO+')]

# # Bug: Direct Credit Entry missing
# # Uncomment this section to add missing data
# dc_entry = [{
#     'Date': pd.Timestamp('2023-09-12'),
#     'Transaction Type': 'Direct Credit',
#     'Description': 'ADVANCED TECHNOLOGIES PTE LTD (EC)',
#     'Amount (RM)': 0.5,
#     'Wallet Balance': 0.5
# }]
# df1 = (
#     pd
#     .concat([df1, pd.DataFrame(dc_entry)], ignore_index=True)
#     .sort_values('Date', kind='mergesort', ascending=False)
#     .reset_index(drop=True)
# )

# Bug: Money Packet Received & Direct Credit (money receive entries) not displaying true bal
# 1. Locating the problematic rows
# 2. Find nearest Non-quick-reload-payment before* the transaction
#    Its impossible to have Quick Reload Payment before* the money receive entries
# 3. After most of the money receive transaction fixed, fix the first* n of money receive entries
# * is in the reversing order
for i, row in df1.iloc[-2::-1].iterrows():
    if row['Transaction Type'] in ['Money Packet Received', 'Direct Credit']:
        # find next balance, skip if next j rows are Quick Reload Payment
        j = i+1
        while df1.at[j, 'Description'] == 'Quick Reload Payment (via GO+ Balance)':
            j += 1
        bal = df1.at[j, 'Wallet Balance']
        df1.at[i, 'Wallet Balance'] = bal + row['Amount (RM)']

i = (~df1['Transaction Type'][::-1].isin(['Money Packet Received', 'Direct Credit'])).idxmax() + 1
while i < df1.shape[0]:
    df1.at[i, 'Wallet Balance'] = df1.at[i-1, 'Wallet Balance'] - df1.at[i-1, 'Amount (RM)']
    i += 1

# Bug: Get index which causing reversing entries
def check_reverse_entry(df1):
    return (
        df1
        .assign(
            prev_bal=lambda x: x['Wallet Balance'].shift(-1),
            **{
                'Amount (RM)': lambda x: np.select([
                    np.round(x['prev_bal']+x['Amount (RM)'], 2)==np.round(x['Wallet Balance'],2),
                    np.round(x['prev_bal']-x['Amount (RM)'], 2)==np.round(x['Wallet Balance'],2)
                ], [
                    x['Amount (RM)'],
                    -x['Amount (RM)']
                ], np.nan)
            }
        )
        .loc[lambda x: x['Amount (RM)'].isna()][:-1]
        .index
        .to_list()
    )

# Bug: Attempt to fix reversing entries
# Only trigger when all condition are met:
# 1. Same date
# 2. Description = Quick Reload Payment (via GO+ Balance), follow by another transaction
# 3. With the same amount in a row
# 4. Must be a positive trasaction: 
#    Current Balance - Current Amount = Previous Balance
# 5. Next transaction must be a negative transaction:
#    A. Flag if Next Amount + Next Balance != Current Balance 
#    or 
#    B. Flag if Next transaction is Quick Reload Payment (via GO+ Balance)
# Check reversed entry again after this attempt
new_idx = []
for i, row in df1.iterrows():
    if (
        0 < i < df1.shape[0]-1 and
        row['Description'] == 'Quick Reload Payment (via GO+ Balance)' and 
        row['Date'] == df1.loc[i+1, 'Date'] and
        row['Amount (RM)'] == df1.loc[i+1, 'Amount (RM)'] and
        np.round(row['Wallet Balance'] - row['Amount (RM)'],2) == np.round(df1.loc[i+1, 'Wallet Balance'],2) and
        # row['Amount (RM)'] != df1.loc[i-1, 'Amount (RM)'] and
        (np.round(df1.loc[i-1, 'Wallet Balance'] + df1.loc[i-1, 'Amount (RM)'],2) != np.round(row['Wallet Balance'],2) or 
        df1.loc[i-1, 'Description'] == 'Quick Reload Payment (via GO+ Balance)')
    ) :
        new_idx.append((i, i+1))
        new_idx.append((i+1, i))

df1 = df1.rename(dict(new_idx)).sort_index()
idx = check_reverse_entry(df1)
check = 0
while len(idx) != 0:
    if check >= 3:
        raise ValueError('Some Entry Not Recorded Properly')
    # Make correction on reversing entries
    new_idx = []
    for k,v in enumerate(idx):
        if k != 0:
            if (diff := (v - idx[k-1])) % 2 == 0:
                for i in range(int(diff/2)):
                    new_idx.append((v-i*2-1, v-i*2))
                    new_idx.append((v-i*2, v-i*2-1))
                idx.remove(v)
            elif idx[k+1] - idx[k-1] == 2:
                new_idx.append((v, v+1))
                new_idx.append((v+1, v))
                idx.remove(idx[k-1])
                idx.remove(v)
            else:
                raise ValueError('Some Entry Not Recorded Properly')
    df1 = df1.rename(dict(new_idx)).sort_index()
    # Rechecking reversing entries
    idx = check_reverse_entry(df1)
    check = check + 1

if len(idx) != 0:
    raise ValueError('Some Entry Not Recorded Properly')

# Final cleaning
df1 = (
    df1
    .assign(
        Description=lambda x: x['Description'].str.replace(r'_\d{5,}', '', regex=True),
        prev_bal=lambda x: x['Wallet Balance'].shift(-1),
        **{
            'Transaction Type': lambda x: np.select(
                [x['Transaction Type']=='DUITNOW_TRANS FERTO'], 
                ['DUITNOW_TRANSFERTO'], 
                x['Transaction Type']),
            'Amount (RM)': lambda x: np.select([
                np.round(x['prev_bal']+x['Amount (RM)'], 2)==x['Wallet Balance'],
                np.round(x['prev_bal']-x['Amount (RM)'], 2)==x['Wallet Balance']
            ], [
                x['Amount (RM)'],
                -x['Amount (RM)']
            ], x['Amount (RM)'])
        }
    )
    .drop(['prev_bal', 'Wallet Balance'], axis=1)
    .iloc[::-1]
    .query('~Description.str.contains("GO+", regex=False)')
)

df2 = (
    df2
    .assign(
        **{
            'Amount (RM)': lambda x: np.where(
                              x['Transaction Type']=='GO+ Cash Out',
                              -x['Amount (RM)'],
                              x['Amount (RM)']
                          )
        }
    )
    .drop('Wallet Balance', axis=1)
    .query('~Description.str.contains("eWallet", regex=False)')
)

# Merge both trxs and export to csv
(
    pd
    .concat([df1, df2])
    .sort_values('Date', kind='mergesort')
    .to_csv(CSV_LINK, index=False,  encoding='utf-8')
)
