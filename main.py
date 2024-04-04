import platform
import pandas as pd
import numpy as np
import camelot
import time
from enum import Enum

class SystemPlatform(Enum):
    Windows = 1
    Darwin = 2
    Linux = 3

# Add timestamp right at the end of the filename when export to CSV.
# This is to skip file check permission when replacing the file.
time_str = time.strftime("%Y%m%d_%H%M%S")

# Read PDF Statement into a table collection, the areas/regions and columns separators is self-defined
if platform.system() == SystemPlatform.Darwin.name or platform.system() == SystemPlatform.Linux.name:
    PDF_LINK = r'./data/tng_ewallet_transactions.pdf'
    CSV_LINK = f'./output/tng_ewallet_transactions_{time_str}.csv'
elif platform.system() == SystemPlatform.Windows.name:
    PDF_LINK = r'.\data\tng_ewallet_transactions.pdf'
    CSV_LINK = f'.\output\tng_ewallet_transactions_{time_str}.csv'

table = camelot.read_pdf(PDF_LINK, pages='all', flavor='stream',
    table_regions=['20,600,820,50'], table_areas=['20,600,820,50'], 
    columns=['80,140,230,294,460,660,720'], 
    split_text=True, strip_text='\n')

# Merge all tables and clean the data
df = (
    pd
    .concat([tbl.df for tbl in table._tables], ignore_index=True)
    .set_axis(['Date', 'Status', 'Transaction Type', 'Reference', 'Description', 'Details', 'Amount (RM)', 'Wallet Balance'], axis=1)
    .query('Date.str.contains(r"^\d|^$", na=True) & ~Reference.str.contains(r"^$")', engine='python')
    .assign(idx=lambda x: (~x.Date.str.contains('^$')).cumsum())
    .groupby('idx')
    .apply(lambda x: x.apply(lambda y: ' '.join(y.fillna('').astype(str))).str.strip())
    .reset_index(drop=True)
    .drop(['idx', 'Status', 'Reference', 'Details'], axis=1)
    .assign(
        Date=lambda x: pd.to_datetime(x.Date, format=r'%d/%m/%Y'),
        **{
            'Amount (RM)': lambda x: x['Amount (RM)'].str.strip('RM').astype(float),
            'Wallet Balance': lambda x: x['Wallet Balance'].str.strip('RM').astype(float)
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

# Bug: Money Packet Received & Direct Credit not displaying true bal
for i, row in df1.loc[::-1].iterrows():
    if row['Transaction Type'] in ['Money Packet Received', 'Direct Credit']:
        bal = df1.at[i+1, 'Wallet Balance']
        df1.at[i, 'Wallet Balance'] = bal + row['Amount (RM)']

# Bug: Get index which causing reversing entries
def check_reverse_entry(df1):
    return (
        df1
        .assign(
            prev_bal=lambda x: x['Wallet Balance'].shift(-1),
            **{
                'Amount (RM)': lambda x: np.select([
                    np.round(x['prev_bal']+x['Amount (RM)'], 2)==x['Wallet Balance'],
                    np.round(x['prev_bal']-x['Amount (RM)'], 2)==x['Wallet Balance']
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
idx = check_reverse_entry(df1)

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
if len(idx) != 0:
    raise ValueError('Some Entry Not Recorded Properly')

# Final cleaning
df1 = (
    df1
    .assign(
        Description=lambda x: x['Description'].str.replace('_\d{5,}', '', regex=True),
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