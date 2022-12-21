import numpy as np
import pandas as pd

xlsx = pd.ExcelFile(r'.\data\tng_ewallet_transactions.xlsx')

sheets = []
for i, sheet_name in enumerate(xlsx.sheet_names):
    if i == 0:
        df = pd.read_excel(xlsx, sheet_name=sheet_name, skiprows=1, index_col=0)
    else:
        df = pd.read_excel(xlsx, sheet_name=sheet_name, index_col=0).set_axis(['Date', 'Status', 'Transaction Type', 'Reference', 'Description', 'Details', 'Amount (RM)', 'Wallet Balance'], axis=1)

    df = (
        df
        .query('Date.str.contains(r"\d", na=True)', engine='python')
        .assign(idx=lambda x: x.Date.notna().cumsum())
        .groupby('idx')
        .apply(lambda x: x.apply(lambda y: ' '.join(y.fillna('').astype(str))).str.strip())
        .reset_index(drop=True)
        .drop(['idx', 'Status', 'Reference', 'Details'], axis=1)
    )
    sheets.append(df)

df = (
    pd
    .concat(sheets, ignore_index=True)
    .assign(
        Date=lambda x: pd.to_datetime(x.Date, format=r'%d/%m/%Y'),
        **{
            'Amount (RM)': lambda x: x['Amount (RM)'].str.strip('RM').astype(float),
            'Wallet Balance': lambda x: x['Wallet Balance'].str.strip('RM').astype(float)
        }
    )
)

df1 = df.loc[lambda x: ~x['Transaction Type'].str.startswith('GO+')]
df2 = df.loc[lambda x: x['Transaction Type'].str.startswith('GO+')]

# (
#     df1
#     .assign(
#         prev_bal=lambda x: x['Wallet Balance'].shift(-1),
#         **{
#             'Amount (RM)': lambda x: np.select([
#                 np.round(x['prev_bal']+x['Amount (RM)'], 2)==x['Wallet Balance'],
#                 np.round(x['prev_bal']-x['Amount (RM)'], 2)==x['Wallet Balance']
#             ], [
#                 x['Amount (RM)'],
#                 -x['Amount (RM)']
#             ], np.nan)
#         }
#     )
#     .loc[lambda x: x['Amount (RM)'].isna()]
# )

# df1.iloc[0:8]
df1 = df1.rename({6: 7, 7: 6}).sort_index()

df1 = (
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
            ], x['Amount (RM)'])
        }
    )
    .drop(['prev_bal', 'Wallet Balance'], axis=1)
    .iloc[::-1]
    .query('~Description.str.contains("GO+", regex=False)')
)

df2 = (
    df2
    .drop('Wallet Balance', axis=1)
    .query('~Description.str.contains("eWallet", regex=False)')
)
pd.concat([df1, df2]).sort_values('Date', kind='mergesort').to_csv(r'.\output\tng_ewallet_transactions.csv', index=False, encoding='utf-8')

xlsx.close()
