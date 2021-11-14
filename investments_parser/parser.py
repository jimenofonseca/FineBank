from utils.support_functions import calculate_rate_exact_day, calculate_rate_exact_day_cop, \
    calculate_rate_exact_day_cop_inversed
from decimal import Decimal
import os
import pandas as pd
from settings import CURRENCIES


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
        #print(year,rate, month,value, from_currency, to_currency)
        new_with = Decimal(str(round(rate, 4))) * Decimal(str(round(value, 4)))
        return new_with


def main():
    # get directories
    from directories_pointer import directories
    directory = directories()

    # get location of input directory
    DIRECTORY_INVESTMENTS = directory["DIRECTORY_INVESTMENTS"]

    # get location of output files
    DATA_PROCESSED_INVESTMENTS = directory["DATA_PROCESSED_INVESTMENTS"]

    # get location of output file
    DATA_PROCESSED_INVESTMENTS_METADATA = directory["DATA_PROCESSED_INVESTMENTS_METADATA"]

    # process data
    # get list of all excel files in there (it avoids hidden files):
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(DIRECTORY_INVESTMENTS) if
                 (isfile(join(DIRECTORY_INVESTMENTS, f)) and f.endswith('.xlsx') and not f.startswith('~'))]

    # iterate over every file name
    registry_accounts = []  # here we collect the name of the accounts we have read
    registry_currency_per_account = []  # here we collect the currency of every account
    registry_type_per_account = []  # here we collect the type of every account
    registry = pd.DataFrame()  # here we collecte th
    for file in onlyfiles:
        file_path = os.path.join(DIRECTORY_INVESTMENTS, file)
        xls = pd.ExcelFile(file_path)
        accounts = xls.sheet_names
        accounts.remove('VAL')  # so it does not provide the hidden sheet.
        print('Reading the next accounts %s from file %s' % (accounts, file))
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

    # populate fields month and year
    s = pd.to_datetime(registry['DATE'], errors="coerce", format='%Y-%m-%d %H:%M:%S')
    s = s.fillna(pd.to_datetime(registry['DATE'], format='%d/%m/%Y', errors='coerce'))
    registry['DATE'] = s
    registry["MONTH"] = registry['DATE'].dt.month_name().str.slice(stop=3)  # add month to the database
    registry['YEAR'] = registry['DATE'].dt.year  # add year to the database

    # compute the new fields per currency
    for currency in CURRENCIES.values():
        columns_to_transform = ["CREDIT", "DEBIT", "BALANCE"]
        for column in columns_to_transform:
            registry[column + "_" + currency] = registry[["YEAR", "MONTH", column, "CURRENCY"]].apply(
                lambda x: conversion(x, currency), axis=1)

    # save processed data to disk
    registry.to_csv(DATA_PROCESSED_INVESTMENTS)

    # save the accounts, their type and their currency as a data_frame
    registry_metadata = pd.DataFrame({"ACCOUNT": registry_accounts,
                                       "TYPE": registry_type_per_account,
                                       "CURRENCY": registry_currency_per_account})
    registry_metadata.to_csv(DATA_PROCESSED_INVESTMENTS_METADATA)
    print("success!")


if __name__ == '__main__':
    main()
