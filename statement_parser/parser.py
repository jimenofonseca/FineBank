from statement_parser.preproccessing import DBS_parser
from statement_parser.preprocessing_post import POSTFINANCE_parser
from utils.support_functions import calculate_rate_exact_day, calculate_rate_exact_day_cop, \
    calculate_rate_exact_day_cop_inversed
from settings import CURRENCIES
from decimal import Decimal
import pandas as pd
import os


def conversion(x, to_currency):
    year = x[0]
    month = x[1]
    value = x[2]
    from_currency = x[3]

    # in case it is the same currency
    if from_currency == to_currency:
        return Decimal(value)

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
        new_with = Decimal(str(round(rate, 4))) * Decimal(value)
        return new_with


def main():
    # get directories
    from directories_pointer import directories
    directory = directories()
    DIRECTORY_POSTFINANCE = directory["DIRECTORY_POSTFINANCE"]
    DIRECTORY_DBS = directory["DIRECTORY_DBS"]
    DATA_PROCESSED_BANKING = directory["DATA_PROCESSED_BANKING"]
    DATA_PROCESSED_BANKING_METADATA = directory["DATA_PROCESSED_BANKING_METADATA"]

    # process data from singapore and and swiss accounts
    if os.path.isdir(DIRECTORY_POSTFINANCE) or os.path.isdir(DIRECTORY_DBS):
        if os.path.isdir(DIRECTORY_POSTFINANCE):
            registry_postfinance, registry_postfinance_metadata = POSTFINANCE_parser(DIRECTORY_POSTFINANCE, directory)
            print('We detected data for Postfinance Banking, we are proceeding to parse it')
        else:
            registry_postfinance = pd.DataFrame()
            registry_postfinance_metadata = pd.DataFrame()
            print('We did not detected any data for Postfinance Banking')

        if os.path.isdir(DIRECTORY_DBS):
            registry_dbs, registry_dbs_metadata = DBS_parser(DIRECTORY_DBS, directory)
            print('We detected data for DBS Banking, we are proceeding to parse it')
        else:
            registry_dbs = pd.DataFrame()
            registry_dbs_metadata = pd.DataFrame()
            print('We did not detected any data for DBS Banking')
    else:
        Exception(
            "we did not find any data to parse, make sure you have one of these folders: BANKING/DBS or BANKING/POSTFINANCE")

    # append the two databases if existent
    registry = pd.concat([registry_dbs, registry_postfinance], ignore_index=True, sort=False)
    registry_metadata = pd.concat([registry_postfinance_metadata, registry_dbs_metadata], ignore_index=True, sort=False)

    # populate fields month and year
    registry['DATE'] = pd.to_datetime(registry['DATE'], format='%d%b%Y:%H:%M:%S.%f')
    registry["MONTH"] = registry['DATE'].dt.month_name().str.slice(stop=3)  # add month to the database
    registry["YEAR"] = registry['DATE'].dt.year  # add year to the database

    # compute the new fields per currency
    for currency in CURRENCIES.values():
        columns_to_transform = ["CREDIT", "DEBIT", "BALANCE"]
        for column in columns_to_transform:
            registry[column + "_" + currency] = registry[["YEAR", "MONTH", column, "CURRENCY"]].apply(
                lambda x: conversion(x, currency), axis=1)

    # save processed data to disk
    registry.to_csv(DATA_PROCESSED_BANKING)

    # save the accounts, their type and their currency as a data_frame
    registry_metadata.to_csv(DATA_PROCESSED_BANKING_METADATA)
    print("succeed!")


if __name__ == '__main__':
    main()
