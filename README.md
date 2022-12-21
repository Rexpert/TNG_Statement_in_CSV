# TNG Statement in CSV
This code builds a CSV table that records all transactions within TNG e-Wallet from its statement.

# Usage
1. Clone this repo.
2. You need to install [Python 3](https://www.python.org/) and its relevant dependencies:
    - [`camelot`](https://camelot-py.readthedocs.io/en/master/) - to read PDF statement
    - [`pandas`](https://pandas.pydata.org/docs/index.html) - data manipulation
    - Optional: [`matplotlib`](https://matplotlib.org/) - visualize the page and [visual debug](https://camelot-py.readthedocs.io/en/master/user/advanced.html#visual-debugging) the table generation
3. Download your TNG statement (which is named `tng_ewallet_transactions.pdf`) and locating it into a `data` folder
4. Run the [main.py](main.py)
5. Get your transaction table named `tng_ewallet_transactions.csv` in `output` folder.

# Disclaimer
1. I don't work in [Touch 'n Go](https://www.touchngo.com.my/) company, and hence do not represent Touch 'n Go.
2. This repository is my work to ease myself in analyzing my own expenses in Touch 'n Go e-Wallet. But you can freely use it and welcome to contribute, you are helping me to make this code more meaningful.
3. Please consider use this code in your own responsibility, although it is not harmful at all.

MIT [@Rexpert](https://github.com/Rexpert) 2022
