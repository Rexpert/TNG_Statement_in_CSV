import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import camelot
import os

# PDF_LINK = os.path.join('pdf', 'tng_ewallet_transactions.pdf')
PDF_LINK = os.path.join('pdf', 'transactions-13-10-2024-154730.pdf')

table = camelot.read_pdf(PDF_LINK, pages='2', flavor='stream',
            table_regions=['40,710,560,0'], table_areas=['40,710,560,0'],
            columns=['170,295,423'], 
            split_text=True, strip_text='\n')

table._tables[0].df


fig, ax = plt.subplots()
pg = camelot.plot(table[0], kind='text')
yaxis = plt.gca().yaxis
yaxis.set_major_locator(MultipleLocator(10))
xaxis = plt.gca().xaxis
xaxis.set_major_locator(MultipleLocator(10))
xaxis.set_tick_params(labelrotation=90)
plt.grid(True)
pg.show()