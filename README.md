# The FineBank

A simple, yet powerful open source app to keep track of personal finances. Made for family and friends and free to use.

## Features

It includes some cool features such as:

1. Parser of PDF statements for Banking Accounts in DBS (Singapore) and Postfinance (Switzerland) to excel.
2. Categorization of transactions from typical retailers (i.e., Swsscome == Bills, Yoga == Health)
3. Login interface (set password for family members).
4. Interactive charts Income, Expenses, Net worth, Investments and other assets (Bonds, Real Estate, retirement, deposits etc...)
5. Multi-currency (according to FOREX current exchange rate).
6. Absolutely free.

DICLAIMER: ALL DATA HAS BEEN RANDOMLY GENERATED AND IT IS PRESENTED FOR DEMONSTRATION PURPOSES.

### Parser of banking statments

### Overview Panel

![OVERVIEW](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/all/Screenshot%202019-04-19%20at%2010.52.09%20AM.png)

### Cash accounts Panel

!['CASH'](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/all/Screenshot%202019-04-19%20at%2010.04.22%20AM.png)

### Investments Panel

!['INVESTMENTS'](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/all/Screenshot%202019-04-19%20at%2010.04.45%20AM.png)

### Net-worth Panel

![NETWORTH](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/all/Screenshot%202019-04-19%20at%2010.04.56%20AM.png)

### Parser of Bank statements to excel

![PARSER](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/all/parser2.png)

# Installation:

1. Download the App for Mac OX (no need of anything more).
2. Open it, it will install automatically the first time.
3. Connection to the internet to use the Bank statment parsers. The app needs to compute the excahnge rate for multiple currencies.

# Manual

## do a quick test:

1. Get the example_data included in this repository from [here](https://github.com/JIMENOFONSECA/FineBank/raw/master/example_data/example_data.zip)
2. Open the FineBank App.
3. Indicate the location of your database and the name of it. For the screenshots I used the example_database. It is a randomly generated database I included in this repository. 
4. Provide the credentials for login: These are `USERNAME` add `PASSWORD` = TheFineBankAppbyJimeno

![Login](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/Login/login.gif)

5. Click on the button `run the dashboard`.

![Overview](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/Overview%20tab/overview.gif)

If all diagrams are showing, then the tool is working! now you can do other stuff, like parsing and visualizing your own data.

## Prepare your financial data

The first step is to prepare your financial data in a format that can be understood by the FineBank app. It is the most time-consuming part of the excercise, but it should become handy in further versions.

1. Get the example_data included in this repository from [here](https://github.com/JIMENOFONSECA/FineBank/raw/master/example_data/example_data.zip)
2. Navigate to `example_data/INPUTS/BANKING`.
3. Store your statementes from DBS in the DBS folder. Alternatively store your statements form Postfinance in the Postfinance folder.

![INPUTS_BANK](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/input%20bank%20folder/bank2.gif)

4. After that, Navigate to `example_data/INPUTS/INVESTMENTS.`
5. Use the excel file in `example_data/INPUTS/INVESTMENTS` to input and categorize your investments.
6. To create a new acount or type of investment just create a new worksheet in the excel file. The FineBAnk App will use the name of the worksheet as the name of the investment.

![INPUTS_INVESTMENTS](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/input%20investments/investments.gif)

6. As a last step you will need to configure the `CATEGORIES.XLS` file. the file stores a relation of categories and vendors. This will help the tool to more accurrately categorize your data.

![INPUTS_CATEGORIES](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/input%20categories/categories.gif)


## Process your financial data

The next step is to open the app and process the data you have. Follow the next steps:

1. Open the FineBank App.
2. Indicate the location of your database and the name of it. For the screenshots I used the example_database. It is a randomly generated database I included in this repository. 
3. Provide the credentials for login: These are `USERNAME` and `PASSWORD` = TheFineBankAppbyJimeno

![Login](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/Login/login.gif)

4. click the button `parse cash accounts`. Wait until finished. It might take a while if you have many statements.
5. click the button `parse investments`. Wait until finished. This is quite fast.how I misspelled `outputs`. Sorry about that!.

![outputs](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/Outputs/outputs.gif)


## Visualize the outputs

4. Navigate to the login page, put the credential in and then click on `run the dashboard`.
 - This dashboard presents a general view to your finances. 
 - You can select one or multiple years to see.
 - You can also selecte the currency.
 - You can also turn off-on any label. The Charts are fully interactive

![Overview](https://github.com/JIMENOFONSECA/FineBank/raw/master/screenshots/Overview%20tab/overview.gif)

MORE IN A FEW WEEKS TIME
