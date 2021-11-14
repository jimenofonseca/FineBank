from utils.support_functions import calculate_rate_exact_day, calculate_rate_exact_day_cop, \
    calculate_rate_exact_day_cop_inversed
from decimal import Decimal
import os
import pandas as pd
from settings import CURRENCIES, calc_categories
from statement_parser.preproccessing import get_category


def conversion(x, to_currency):
    year = x[0]
    month = x[1]
    value = x[2]
    from_currency = x[3]

    # in case it is the same currency
    if from_currency == to_currency:
        return Decimal(str(round(value, 4)))

    # in case we have COP (not suppported with daily rates)
    if from_currency == 'COP':  # we use an approximated way:
        rate = calculate_rate_exact_day_cop(to_currency)
    elif to_currency == 'COP':  # we use an apporximated way:
        rate = calculate_rate_exact_day_cop_inversed(from_currency)
    else:
        rate = calculate_rate_exact_day(from_currency, month, year, to_currency)

    if value == "":
        return value
    else:
        #print(year,month,value, rate, from_currency, to_currency)
        new_with = Decimal(str(round(rate, 4))) * Decimal(str(round(value, 4)))
        return new_with


def MANUAL_parser(file_path, directories):

    CATEGORIES, CATEGORIES_DEPOSIT, CATEGORIES_WITHDRAWAL = calc_categories(directories)

    # process data
    registry_accounts = []  # here we collect the name of the accounts we have read
    registry_currency_per_account = []  # here we collect the currency of every account
    registry_type_per_account = []  # here we collect the type of every account
    registry = pd.DataFrame()  # here we collecte th
    xls = pd.ExcelFile(file_path)
    accounts = xls.sheet_names
    print('Reading the next accounts %s from file %s' % (accounts, file_path))
    registry_accounts.extend(accounts)
    for account in accounts:

        # read it
        data_account = pd.read_excel(file_path, account)

        # calculate fields
        data_account["ACCOUNT"] = account  # add name of account to the database

        # get currency and add it to registry_currency_per_account list
        currency_account = list(set(data_account["CURRENCY"].values))  # get currency of account
        type_account = list(set(data_account["TYPE"].values))  # get currency of account

        if len(
                currency_account) > 1:  # whatch out, you are indicating two currencies for the same account. not possible
            Exception(
                "The account %s has two or more currencies %s, that is not supported" % (account, currency_account))
        elif len(
                type_account) > 1:  # whatch out, you are indicating two currencies for the same account. not possible
            Exception("The account %s has two or more types %s, that is not supported" % (account, type_account))
        else:
            registry_currency_per_account.append(currency_account[0])
            registry_type_per_account.append(type_account[0])

        # add account to data_frame of accounts:
        registry = registry.append(data_account, ignore_index=True, sort=False)

    # category assignment
    withdrawal_boolean = [True if x > 0 and y <= 0 else False for x,y in zip(registry["DEBIT"].values, registry["CREDIT"].values)]
    registry["CAT"], _, _, _ = get_category(registry["DESC_1"],
                                            registry["DESC_1"],
                                            registry["DESC_1"],
                                            withdrawal_boolean,
                                            CATEGORIES)

    # sget metadata
    registry_metadata = pd.DataFrame({"ACCOUNT": registry_accounts,
                                      "TYPE": registry_type_per_account,
                                      "CURRENCY": registry_currency_per_account})


    return registry, registry_metadata
