import os
import camelot
from PyPDF2 import PdfFileReader
import pandas as pd
from re import sub
from decimal import Decimal
import numpy as np
import datetime
from settings import MONTH_ORDER, calc_categories, MONTH_ORDER_DBS_2021, MONTH_ORDER_DBS_2021_MAP
from statement_parser.preprocessing_post import getListOfFiles



PAGES_BEGINNING = 1  # pages to skip at the beginning of the statment
PAGES_END = 1  # pages to skip at the end of the statement


def Parser_function(filepath, year_str, CATEGORIES):

    # get number of pages
    pdf = PdfFileReader(open(filepath, 'rb'))
    pages_pdf = pdf.getNumPages()

    # get iterator and empy series to fill in
    range_of_pages = range(PAGES_BEGINNING, pages_pdf - PAGES_END)
    date_str = []
    withdrawal_Decimal = []
    deposit_Decimal = []
    balance_Decimal = []
    description_str = []
    description2_str = []
    description3_str = []
    withdrawal_boolean = []
    index_where_total_is = []
    real_year = []
    real_month = []
    # go over each page and extract data
    for page in range_of_pages:

        if index_where_total_is != []:  # if total is in the end of the page
            break

        print("Page No. ", page + 1)
        # read pdf into dataframe
        page_table_format = camelot.read_pdf(filepath, pages=str(page + 1), flavor='stream',
                                             table_areas=['20,640,700,50'])
        dataframe_table = page_table_format[0].df

        # indicate if total is in first column, this means there is an error and the region needs to change
        index_where_total_is2 = dataframe_table.index[dataframe_table[0] == "Total"].tolist()
        index_where_total_is3 = dataframe_table.index[dataframe_table[0] == "Total Balance Carried Forward in SGD:"].tolist()
        if index_where_total_is2 != [] or index_where_total_is3 != []:
            print("read 3 columns, 4 expected, correcting...")
            page_table_format = camelot.read_pdf(filepath, pages=str(page + 1), flavor='stream',
                                                 table_areas=['20,640,700,200'])
            dataframe_table = page_table_format[0].df
            index_where_total_is2 = dataframe_table.index[dataframe_table[0] == "Total"].tolist()
            index_where_total_is3 = dataframe_table.index[dataframe_table[0] == "Total Balance Carried Forward in SGD:"].tolist()

        if index_where_total_is2 != [] or index_where_total_is3 != []:
            print("read 3 columns, 4 expected, correcting...")
            page_table_format = camelot.read_pdf(filepath, pages=str(page + 1), flavor='stream',
                                                 table_areas=['20,610,700,200'])
            dataframe_table = page_table_format[0].df
            index_where_total_is2 = dataframe_table.index[dataframe_table[0] == "Total"].tolist()
            index_where_total_is3 = dataframe_table.index[dataframe_table[0] == "Total Balance Carried Forward in SGD:"].tolist()





        # take out the last part
        #adapting this so it can read the statements of 2021
        try:
            # indicate where the total is, to be used in the next loop
            index_where_total_is = dataframe_table.index[dataframe_table[1] == "Total"].tolist()
            index_where_account_is = dataframe_table.index[dataframe_table[1] == "Balance Carried Forward"].tolist()
            dataframe_table_raw = dataframe_table.drop(dataframe_table.index[index_where_account_is[0] + 2:])

            # select the number of column with witdrawal
            columns_number = dataframe_table.shape[1]
            for column_index in range(columns_number):
                if "Withdrawal" in dataframe_table.loc[:, column_index].values:
                    with_column_index = column_index
                if "Deposit" in dataframe_table.loc[:, column_index].values:
                    depo_column_index = column_index
                if "Balance" in dataframe_table.loc[:, column_index].values:
                    balance_column_index = column_index
                if "Description" in dataframe_table.loc[:, column_index].values:
                    desc_column_index = column_index

        except Exception:
            index_where_account_is = dataframe_table.index[dataframe_table[1] == "Total Balance Carried Forward in SGD:"].tolist()
            index_where_it_starts_is = dataframe_table.index[dataframe_table[1] == "Balance Brought Forward"].tolist()
            dataframe_table_raw = dataframe_table.drop(dataframe_table.index[index_where_account_is[0] + 2:])
            dataframe_table_raw = dataframe_table_raw.drop(dataframe_table_raw.index[:index_where_it_starts_is[0]+1])
            dataframe_table_raw.reset_index(inplace=True, drop=True)
            # indicate where the total is, to be used in the next loop
            index_where_total_is = dataframe_table_raw.index[dataframe_table_raw[1] == "Total Balance Carried Forward in SGD:"].tolist()

            # select the number of column with witdrawal
            columns_number = dataframe_table.shape[1]
            for column_index in range(columns_number):
                if "Withdrawal (-)" in dataframe_table.loc[:, column_index].values:
                    with_column_index = column_index
                if "Deposit (+)" in dataframe_table.loc[:, column_index].values:
                    depo_column_index = column_index
                if "Balance" in dataframe_table.loc[:, column_index].values:
                    balance_column_index = column_index
                if "Description" in dataframe_table.loc[:, column_index].values:
                    desc_column_index = column_index

        # indicate the total of withdrawals and deposits:
        if index_where_total_is != []:
            index = index_where_total_is[0]
            withdrawal_total_decimal = Decimal(sub(r'[^\d.]', '', dataframe_table_raw.loc[index, with_column_index]))
            deposit_total_decimal = Decimal(sub(r'[^\d.]', '', dataframe_table_raw.loc[index, depo_column_index]))

        # start filling in data
        len_dataframe = dataframe_table_raw.shape[0]
        for row in range(len_dataframe):
            date = dataframe_table_raw.loc[row, 0]
            description = dataframe_table_raw.loc[row, 1]
            if date != '' and (description != "Balance Carried Forward" or description != "Total Balance Carried Forward in SGD"):
                length_date = len(date.split())
                length_date_2021 = len(date.split("/"))
                if length_date == 2 or length_date_2021 == 3:
                    if length_date == 2:
                        if date.split()[1] in MONTH_ORDER:
                            date_withyear = date + " " + year_str
                            date_withyear_formatted = datetime.datetime.strptime(date_withyear, '%d %b %Y')
                            real_month.append(date.split()[1])
                    elif length_date_2021 == 3:
                        if date.split("/")[1] in MONTH_ORDER_DBS_2021:
                            date_withyear = date
                            date_withyear_formatted = datetime.datetime.strptime(date_withyear, '%d/%m/%Y')
                            real_month.append(MONTH_ORDER_DBS_2021_MAP[date.split("/")[1]])

                    real_year.append(year_str)
                    date_str.append(date_withyear_formatted)

                    # withdrawal and deposit
                    if dataframe_table_raw.loc[row, with_column_index] == '':
                        withdrawal_Decimal.append(Decimal(0.0))
                        withdrawal_boolean.append(False)
                    else:
                        balance_Decimal.append(dataframe_table_raw.loc[row, balance_column_index].replace(",", ""))
                        withdrawal_Decimal.append(
                            Decimal(sub(r'[^\d.]', '', dataframe_table_raw.loc[row, with_column_index])))
                        withdrawal_boolean.append(True)

                    if dataframe_table_raw.loc[row, depo_column_index] == '':
                        deposit_Decimal.append(Decimal(0.0))
                    else:
                        balance_Decimal.append(dataframe_table_raw.loc[row, balance_column_index].replace(",", ""))
                        deposit_Decimal.append(
                            Decimal(sub(r'[^\d.]', '', dataframe_table_raw.loc[row, depo_column_index])))

                    # accumulate balance if the last value was ''
                    if balance_Decimal != []: #avovid problems ab June 2022 in DBS
                        if balance_Decimal[-1] == '':
                            if len(balance_Decimal) > 1:
                                balance_Decimal[-1] = balance_Decimal[-2]
                            else:
                                balance_Decimal[-1] = dataframe_table_raw.loc[row - 1, balance_column_index].replace(
                                    ",", "")
                                if balance_Decimal[-1] == '':
                                    balance_Decimal[-1] = dataframe_table_raw.loc[
                                        row - 2, balance_column_index].replace(",", "")

                    if dataframe_table_raw.loc[row, depo_column_index] == '' and dataframe_table_raw.loc[
                        row, with_column_index] == '':
                        balance_Decimal.append(dataframe_table_raw.loc[row, balance_column_index].replace(",", ""))

                    # descriptions
                    description_str.append(dataframe_table_raw.loc[row, desc_column_index])

                    if dataframe_table_raw.loc[row + 1, 0] == '':
                        description2_str.append(dataframe_table_raw.loc[row + 1, desc_column_index])
                    else:
                        description2_str.append('')

                    try:
                        if dataframe_table_raw.loc[row + 2, 0] == '':
                            description3_str.append(dataframe_table_raw.loc[row + 2, desc_column_index])
                        else:
                            description3_str.append('')
                    except:
                        description3_str.append('')

    # category assignment
    category_final2, category1_str, category2_str, category3_str = get_category(description2_str, description3_str,
                                                                                description_str, withdrawal_boolean,
                                                                                CATEGORIES)

    # assertment data
    if sum(withdrawal_Decimal) != withdrawal_total_decimal:
        print("Warning, the total of withdrawals does not match")

    if sum(deposit_Decimal) != deposit_total_decimal:
        print("Warning, the total of deposits does not match")

    statement_df = pd.DataFrame({"DATE": date_str,
                                 "CREDIT": withdrawal_Decimal,
                                 "DEBIT": deposit_Decimal,
                                 "BALANCE": balance_Decimal,
                                 "YEAR": real_year,
                                 "MONTH": real_month,
                                 "DESC_1": description_str,
                                 "DESC_2": description2_str,
                                 "DESC_3": description3_str,
                                 "CAT": category_final2,
                                 "CAT1": category1_str,
                                 "CAT2": category2_str,
                                 "CAT3": category3_str})
    return statement_df


def get_category(description2_str, description3_str, description_str,
                 withdrawal_boolean, CATEGORIES):
    category_final = []
    category_final2 = []

    category1_str = np.vectorize(Categorization)(description_str, CATEGORIES)
    category2_str = np.vectorize(Categorization)(description2_str, CATEGORIES)
    category3_str = np.vectorize(Categorization)(description3_str, CATEGORIES)

    # get confirmation form the three subcategories
    describe = zip(category1_str, category2_str, category3_str)
    for cat1, cat2, cat3 in describe:
        if cat1 == "No Category" and cat2 == "No Category" and cat3 != "No Category":
            category_final.append(cat3)
        elif cat1 == cat2:
            category_final.append(cat1)
        elif cat2 != "No Category" and cat1 == "No Category":
            category_final.append(cat2)
        elif cat1 != "No Category":
            category_final.append(cat1)
        else:
            category_final.append("No Category")

    # get confirmation form the three subcategories
    for cat, width in zip(category_final, withdrawal_boolean):
        if cat == "No Category" and width == True:
            category_final2.append("Unknown Withdrawal")
        elif cat == "No Category" and width == False:
            category_final2.append("Unknown Deposit")
        else:
            category_final2.append(cat)

    return category_final2, category1_str, category2_str, category3_str


def mysplit(s):
    head = s.rstrip('0123456789')
    tail = s[len(head):]

    return head, tail


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def Categorization(description_str, CATEGORIES):
    # categorize full phrases
    cat_flag = True
    for category_str, names_inside_category in CATEGORIES.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if description_str in names_inside_category:
            cat = category_str
            cat_flag = False

    # categorize first word
    if cat_flag:
        for category_str, names_inside_category in CATEGORIES.items():
            description_split = description_str.split(" ")[
                0]  # for name, age in dictionary.iteritems():  (for Python 2.x)
            if description_split in names_inside_category:
                cat = category_str
                cat_flag = False

    # if after the coma the first word matches
    if cat_flag:
        for category_str, names_inside_category in CATEGORIES.items():
            description_split = description_str.split(",")
            lenght_words = len(description_split)
            if lenght_words > 1:  # (for Python 2.x)
                if description_split[1].split()[0] in names_inside_category:
                    cat = category_str
                    cat_flag = False

    # Check if there were payments in foreing currency (generally they are at the end)
    if cat_flag:
        for category_str, names_inside_category in CATEGORIES.items():
            description_split = description_str.split()
            lenght_words = len(description_split)
            if lenght_words == 2 and hasNumbers(description_split[1]):
                description_split = description_split[-1][:3]
                if description_split in names_inside_category:
                    cat = category_str
                    cat_flag = False

    # Check if there were payments in foreing currency (some are at the beginning)
    if cat_flag:
        for category_str, names_inside_category in CATEGORIES.items():
            description_split = description_str.split()
            lenght_words = len(description_split)
            if lenght_words == 1 and hasNumbers(description_split[0]):
                description_split = description_split[-1][:3]
                if description_split in names_inside_category:
                    cat = category_str
                    cat_flag = False

    # last resource, if the word is anywhere
    if cat_flag:
        for category_str, names_inside_category in CATEGORIES.items():
            description_split = description_str.split(" ")
            lenght_words = len(description_split)
            if lenght_words > 1:  # (for Python 2.x)
                for word in description_split:
                    if word in names_inside_category:
                        cat = category_str
                        cat_flag = False

    if cat_flag:
        cat = "No Category"

    return cat


def Metadata(filepath):
    page_table_format = camelot.read_pdf(filepath, pages=str(1), flavor='stream',
                                         table_areas=['20,600,600,200'])
    dataframe_table_raw = page_table_format[0].df

    # small modification so the statements of 2021 can be read
    try:
        date = dataframe_table_raw.loc[0, 0].split('    ')[2]
        month_str = date.split()[-2]
        year_str = date.split()[-1]
        date_statement_str = date.split()[-3] + " " + month_str + " " + year_str
        index_where_account_is = dataframe_table_raw.index[dataframe_table_raw[1] == "Account Number"].tolist()
        account_str = dataframe_table_raw.loc[index_where_account_is[0] + 1, 1]
        index_where_balance_is = dataframe_table_raw.index[
        dataframe_table_raw[1] == "TOTAL  DEPOSITS – CREDIT"].tolist()
        balance_str = dataframe_table_raw.loc[index_where_balance_is[0], 2]
    except Exception:
        columns = ['120,220,380,500']
        page_table_format = camelot.read_pdf(filepath, pages=str(0 + 1), flavor='stream',
                                             table_areas=['20,600,600,200'],
                                             columns=columns)
        dataframe_table_raw = page_table_format[0].df
        date = dataframe_table_raw.loc[0, 0].split(" ")[-3:]
        month_str = date[1]
        year_str = date[2]
        date_statement_str = date[0] + " " + month_str + " " + year_str
        index_where_account_is = dataframe_table_raw.index[dataframe_table_raw[2] == "Account No."].tolist()
        account_str = dataframe_table_raw.loc[index_where_account_is[0] + 2, 2]
        index_where_balance_is = dataframe_table_raw.index[dataframe_table_raw[4] == "Balance"].tolist()
        balance_str = dataframe_table_raw.loc[index_where_balance_is[0] + 2, 4]

    return date_statement_str, month_str, year_str, account_str, balance_str


def DBS_parser(DIRECTORY, directories):

    CATEGORIES, CATEGORIES_DEPOSIT, CATEGORIES_WITHDRAWAL = calc_categories(directories)
    registry = pd.DataFrame()
    # process data
    # get list folders which indicate the years:
    all_files_paths = getListOfFiles(DIRECTORY)
    registry_accounts = []
    for filepath in all_files_paths:

        # extract account number, balance and month of statement form the first page
        print("Working on file {}".format(filepath.split("/")[-1]))
        date_statement_str, month_str, year_str, account_str, balance_str = Metadata(filepath)
        registry_accounts.append(account_str)

        print("Working on statement {} of the account No. {}".format(date_statement_str, account_str))
        # Iterate over the pages of the statement
        statement_df = Parser_function(filepath, year_str, CATEGORIES)

        statement_df["ACCOUNT"] = account_str
        statement_df["STATEMENT"] = date_statement_str
        statement_df["TYPE"] = "CASH"
        statement_df["CURRENCY"] = "SGD"

        registry = pd.concat([registry, statement_df], ignore_index=True)

    registry_accounts = list(set(registry_accounts))
    registry_metadata = pd.DataFrame({"ACCOUNT": registry_accounts,
                                       "TYPE": ["CASH"]*len(registry_accounts),
                                       "CURRENCY": ["SGD"]*len(registry_accounts)})

    return registry, registry_metadata
