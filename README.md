# TNG Statement in CSV
This code builds a CSV table that records all transactions within TNG e-Wallet from its statement.

# Usage
1. Clone this repo.
    ```
    git clone https://github.com/Rexpert/TNG_Statement_in_CSV.git
    ```
2. You need to install [Python 3](https://www.python.org/) and its relevant dependencies:
    <details>
      <summary>
        camelot-py: to read PDF statement
      </summary>
      
      - Installation via `pip`
        ```
        pip install camelot-py[cv]
        ```
      - or if you're using conda environment
        ```
        conda install -c conda-forge camelot-py
        ```
      - Detail installation please refer to `camelot-py` [Documentation](https://camelot-py.readthedocs.io/en/master/) 
    </details>
    <details>
      <summary>
        pandas: data manipulation
      </summary>
      
      - Installation via `pip`
        ```
        pip install pandas
        ```
      - or if you're using conda environment
        ```
        conda install -c conda-forge pandas
        ```
      - Detail installation please refer to `pandas` [Documentation](https://pandas.pydata.org/docs/index.html) 
    </details>
    <details>
      <summary>
        matplotlib: page visualization (Optional)
      </summary>
      
      - Installation via `pip`
        ```
        pip install matplotlib
        ```
      - or if you're using conda environment
        ```
        conda install -c conda-forge matplotlib
        ```
      - [Visual Debug](https://camelot-py.readthedocs.io/en/master/user/advanced.html#visual-debugging) on table generation
      - Detail installation please refer to `matplotlib` [Documentation](https://matplotlib.org/) 
    </details>
    <details open>
      <summary>
        Recommended setup:
      </summary>
      
      | Installation | Version | 
      | ------------ | :-----: |
      | `python`     | 3.9.12  |
      | `camelot-py` | 0.10.1  |
      | `pandas`     | 1.4.3   |
      | `matplotlib` | 3.5.2   |
    </details>
3. Download your TNG statement (which is named `tng_ewallet_transactions.pdf`) and locating it into a `data` folder
4. Run the [main.py](main.py)
    ```
    python main.py
    ```
5. Get your transaction table named `tng_ewallet_transactions.csv` in `output` folder.

# Disclaimer
1. I don't work in [Touch 'n Go](https://www.touchngo.com.my/) company, and hence do not represent Touch 'n Go.
2. This repository is my work to ease myself in analyzing my own expenses in Touch 'n Go e-Wallet. But you can freely use it and welcome to contribute, you are helping me to make this code more meaningful.
3. Please consider use this code in your own responsibility, although it is not harmful at all.

MIT [@Rexpert](https://github.com/Rexpert) 2022
