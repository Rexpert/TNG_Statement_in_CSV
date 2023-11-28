import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import camelot

table = camelot.read_pdf(r'.\data\tng_ewallet_transactions.pdf', pages='44', flavor='stream',
                        table_areas=['20,600,820,50'],
                        columns=['80,140,230,294,460,660,720'], 
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