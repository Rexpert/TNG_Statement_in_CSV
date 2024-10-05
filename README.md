# TNG Statement in CSV
This code builds a CSV table that records all transactions within TNG e-Wallet from its statement.


## How to download TNG Ewallet Statement

> Do not go to [Touch'n Go Web Portal](https://tngportal.touchngo.com.my/#login), it's unrelated to TNG Ewallet

Here're the [official instruction](https://support.tngdigital.com.my/hc/en-my/articles/360035649754-How-can-I-view-or-download-my-transaction-history) provided by Touch'n Go in TNG eWallet app. 

<img src="./images/transaction_1.jpeg" width=450/>
<img src="./images/transaction_2.jpeg" width=450/>

The instruction above is little bit outdated, a newer flow as of writing time is like:
- go to your "Transactions" in TNG eWallet app
- Click "View All", just need to go to the Transaction History page
- Check top right corner, click "Email"
- You have the option to choose to email Last 90 days transaction history or current search result
- Submit

After wait for awhile you should receive an email from Touch'n Go as shown below:

![email](./images/tng_email.png)

Download the attached PDF, make sure its name is **tng_ewallet_transactions.pdf**, and put this file into `data/` folder of this project.


## Usage
1. Clone this repo to your local.
    ```
    git clone https://github.com/Rexpert/TNG_Statement_in_CSV.git
    ```

2. You need to install [Python 3](https://www.python.org/)

3. Setting Up a Python Virtual Environment with `venv` and Installing Dependencies

    This guide will help you create a Python virtual environment using `venv` and install dependencies from a `requirements.txt` file.

    To create a virtual environment:

    ```bash
    # Create a virtual environment (you can name it '.venv' or something else)
    python -m venv .venv
    ```

    Then, activate the virtual environment.


    ```bash
    # On Windows:
    .\.venv\Scripts\activate

    # On macOS/Linux:
    source .venv/bin/activate
    ```

    Once your virtual environment is activated, install the dependencies listed in `requirements.txt` by running:

    ```bash
    pip install -r requirements.txt
    ```

    When you’re done working, you can deactivate the virtual environment by running:

    ```bash
    deactivate
    ```

    This will deactivate the current environment and return you to your system’s default Python environment.

4. Packages

    Recommended setup

    | Installation    | Version | 
    | --------------- | :-----: |
    | `python`        | 3.9.12  |
    | `camelot-py`    | 0.10.1  |
    | `pandas`        | 1.4.3   |
    | `opencv-python` | 4.9.0   |
    | `matplotlib`    | 3.5.2   |

    <details>
      <summary>
        camelot-py: to read PDF statement
      </summary>

      - Installation via `pip`
        ```
        pip install camelot-py
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
        opencv-python: Handle missing / no module named cv2
      </summary>

      - Installation via `pip`
        ```
        pip install opencv-python
        ```
      - or if you're using conda environment
        ```
        conda install -c conda-forge opencv
        ```
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
    <br/>

5. Download your TNG statement (which is named `tng_ewallet_transactions.pdf`) and locating it into a `data/` folder

6. Run the [main.py](main.py)
    ```
    python main.py
    ```

7. Get your transaction table named `tng_ewallet_transactions.csv` in `output` folder.

## Troubleshoot
Some known bugs happen during the generation of the pdf transaction report by TNG, but the only thing we can do is to manually make correction on the data:  
1. Reverse Entry (Found on [c5156d7](https://github.com/Rexpert/TNG_Statement_in_CSV/commit/c5156d7ae697589971cae36ef3f54497dd2d3ce5))  
   - The latest transaction recorded before an older transaction. 
   - This usually happens during the [Quick Reload Payment](https://www.touchngo.com.my/goplus/#:~:text=What%20is%20Quick%20Reload%20Payment) via Go+. In this scenario, the payment is recorded first, then the reload occurs after.
   - I have implemented an autofix in the code to address this.
   - Example:
     ![image](https://github.com/Rexpert/TNG_Statement_in_CSV/assets/46991185/067e6ffe-28a4-45d0-a566-4219587cc18b)

2. Money Packet Balance (Found on [8fe26a5](https://github.com/Rexpert/TNG_Statement_in_CSV/commit/8fe26a5b2e9884737b0a6bda975054a0f44aaaea))
   - The wallet balance of the money packet entries unexpectedly equals the amount of money packet received.
   - This is happened in the CNY 2023 when the [Money Packet Campaign](https://www.touchngo.com.my/faq/snatch-ang-pow-campaign/) took place.
   - I have implemented an autofix in the code to address this.
   - Example:
     ![image](https://github.com/Rexpert/TNG_Statement_in_CSV/assets/46991185/aa06e93d-480e-4ed1-aa93-d4cbc036b461)

3. Missing Direct Credit entry (Found on [362cc8a](https://github.com/Rexpert/TNG_Statement_in_CSV/commit/362cc8a1362859e0be5d71780b8c2a10ddb62527))
   - Direct Credit entries are not recorded in the transaction history
   - Some of us might be involved in the Weekly Check-in on the A+ reward. The check-in for `9 Sept 2023`, `10 Sept 2023` and `12 Sept 2023` rewards free credits, but the transactions are not recorded in the pdf. However, they can be viewed in the TNG e-Wallet app's history.
   - You need to input those transactions manually if you were involved in those rewards, otherwise the `ValueError: Some Entry Not Recorded Properly` will be raised.
   - Example:
     ![image](https://github.com/Rexpert/TNG_Statement_in_CSV/assets/46991185/f56ea6cd-f798-469a-81db-577d83f8e71b)

4. Other Unknown Bugs
   - Any uncaught bug will raise `ValueError: Some Entry Not Recorded Properly` and exit the code unexpectedly. Please open an issue and attach/screenshot the relevant transaction history pdf if found such case. 

## Disclaimer
1. I don't work in [Touch 'n Go](https://www.touchngo.com.my/) company, and hence do not represent Touch 'n Go.
2. This repository is my work to ease myself in analyzing my own expenses in Touch 'n Go e-Wallet. But you can freely use it and welcome to contribute, you are helping me to make this code more meaningful.
3. Please consider use this code in your own responsibility, although it is not harmful at all.

MIT [@Rexpert](https://github.com/Rexpert) 2022
