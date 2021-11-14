import pandas as pd


def get_options(YEARS_TO_PROCESS, ACCOUNT_TYPE):
    # THIS MAKES SOME USEFUL CALCULATIONS FOR SCRIPTS
    years_options = []
    for year in YEARS_TO_PROCESS:
        years_options.append({'label': year, 'value': year})
    currencies_options = []
    for name, acronym in CURRENCIES.items():
        currencies_options.append({'label': name, 'value': acronym})
    inv_accounts_options = []
    for name, type_account in ACCOUNT_TYPE.items():
        if (name == "BONDS") or (name == "REAL_ESTATE") or (name == "RETIREMENT"):
            for account in type_account:
                inv_accounts_options.append({'label': account, 'value': account})
    cash_accounts_options = []
    accounts_cash = ACCOUNT_TYPE["CASH"]
    for account in accounts_cash:
        cash_accounts_options.append({'label': account, 'value': account})
    bond_accounts_options = []
    accounts_bonds = ACCOUNT_TYPE["BONDS"]
    for account in accounts_bonds:
        bond_accounts_options.append({'label': account, 'value': account})
    rs_accounts_options = []
    accounts_rs = ACCOUNT_TYPE["REAL_ESTATE"]
    for account in accounts_rs:
        rs_accounts_options.append({'label': account, 'value': account})
    retirement_accounts_options = []
    accounts_ret = ACCOUNT_TYPE["RETIREMENT"]
    for account in accounts_ret:
        retirement_accounts_options.append({'label': account, 'value': account})

    return years_options, currencies_options, inv_accounts_options, cash_accounts_options, bond_accounts_options, rs_accounts_options, retirement_accounts_options

def calc_categories(directory):
    excel_file = pd.read_excel(directory["CATEGORIES_DATA"], "CATEGORIES")
    CATEGORIES_DEPOSIT = list(set(excel_file[excel_file["TYPE"] == "DEPOSIT"]["CATEGORY"]))
    CATEGORIES_WITHDRAWAL = list(set(excel_file[excel_file["TYPE"] == "WITHDRAWAL"]["CATEGORY"]))

    categories = list(set(excel_file["CATEGORY"]))
    CATEGORIES_dict = {}
    for category in categories:
        CATEGORIES_dict.update({category: list(set(excel_file[excel_file["CATEGORY"] == category]["FIELD"]))})

    return CATEGORIES_dict, CATEGORIES_DEPOSIT, CATEGORIES_WITHDRAWAL

def calc_accounts(directory):
    DATA_PROCESSED_INVESTMENTS_METADATA = pd.read_csv(directory["DATA_PROCESSED_INVESTMENTS_METADATA"])
    DATA_PROCESSED_BANKING_METADATA = pd.read_csv(directory["DATA_PROCESSED_BANKING_METADATA"])
    meta_data_appended = DATA_PROCESSED_INVESTMENTS_METADATA.append(DATA_PROCESSED_BANKING_METADATA, ignore_index=True)

    types = list(set(meta_data_appended["TYPE"]))
    ACCOUNT_TYPE_dict = {}
    for type in types:
        ACCOUNT_TYPE_dict.update({type: list(set(meta_data_appended[meta_data_appended["TYPE"] == type]["ACCOUNT"]))})


    accounts = list(set(meta_data_appended["ACCOUNT"]))
    ACCOUNTS_CURRENCY_list = {}
    for account in accounts:
        ACCOUNTS_CURRENCY_list.update({account: list(set(meta_data_appended[meta_data_appended["ACCOUNT"] == account]["CURRENCY"]))[0]})

    return ACCOUNT_TYPE_dict, ACCOUNTS_CURRENCY_list


def calc_years(directory):
    DATA_PROCESSED_INVESTMENTS = pd.read_csv(directory["DATA_PROCESSED_INVESTMENTS"])
    DATA_PROCESSED_BANKING = pd.read_csv(directory["DATA_PROCESSED_BANKING"])
    meta_data_appended = DATA_PROCESSED_INVESTMENTS.append(DATA_PROCESSED_BANKING, ignore_index=True, sort=False)

    years = list(set(meta_data_appended["YEAR"]))
    years.sort()
    YEARS_TO_PROCESS = [str(x) for x in years]

    return YEARS_TO_PROCESS

CURRENCIES = {'Singapur Dollar': 'SGD', 'Swiss Franc': 'CHF', 'Colombian Peso': 'COP', 'American Dollar': 'USD'}
MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_ORDER_DBS_2021 = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
MONTH_ORDER_DBS_2021_MAP = dict(zip(MONTH_ORDER_DBS_2021, MONTH_ORDER))


def calc_type(account, ACCOUNT_TYPE):
    for type_cat, name_inside_type in ACCOUNT_TYPE.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if account in name_inside_type:
            return type_cat