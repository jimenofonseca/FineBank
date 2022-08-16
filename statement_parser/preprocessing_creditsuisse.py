import os
import camelot
from PyPDF2 import PdfFileReader
import pandas as pd
from re import sub
from decimal import Decimal
import numpy as np
import datetime
from settings import calc_categories


PAGES_BEGINNING = 0  # pages to skip at the beginning of the statment
PAGES_END = 0  # pages to skip at the end of the statement

conversion_numeric_month = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun", "07": "Jul",
                            "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dez"}


def Parser_function(filepath, CATEGORIES):
    # get number of pages
    pdf = PdfFileReader(open(filepath, 'rb'))
    pages_pdf = pdf.getNumPages()

    # get iterator and empy series to fill in
    range_of_pages = range(PAGES_BEGINNING, pages_pdf - PAGES_END)
    date_str = []
    withdrawal_Decimal = []
    deposit_Decimal = []
    description_str = []
    description2_str = []
    description3_str = []
    withdrawal_boolean = []
    index_where_total_is = []
    real_month = []  # just because some extrats get money from past months.
    real_year = []
    balance_Decimal = []
    # go over each page and extract data
    for page in range_of_pages:

        if index_where_total_is != []:  # if total is in the end of the page
            break

        print("Page No. ", page + 1)
        # read pdf into dataframe
        # set where to check in  the statement
        if page + 1 == 1:  # the first page is always different
            region = ['20,600,700,50']
        else:
            region = ['20,750,700,50']
        page_table_format = camelot.read_pdf(filepath, pages=str(page + 1), flavor='stream',
                                             table_areas=region,
                                             columns=['90,300,400,450,500'])
        dataframe_table = page_table_format[0].df

        # indicate if total is in first column, this means there is an error and the region needs to change
        index_where_total_is2 = dataframe_table.index[dataframe_table[0] == "Umsatztotal / Schlusssaldo"] .tolist()
        if index_where_total_is2 != []:
            print("read 3 columns, 4 expected, correcting...")
            page_table_format = camelot.read_pdf(filepath, pages=str(page + 1), flavor='stream',
                                                 table_areas=['20,750,700,50'])
            dataframe_table = page_table_format[0].df
            index_where_total_is2 = [1]

        if index_where_total_is2 != []:
            print("read 3 columns, 4 expected, correcting...")
            page_table_format = camelot.read_pdf(filepath, pages=str(page + 1), flavor='stream',
                                                 table_areas=['20,610,700,200'])
            dataframe_table = page_table_format[0].df
            index_where_total_is2 = [1]


        if len(dataframe_table.iloc[0]) != 6:
            raise Exception("error, the table does not have the right number of columns, page", str(page + 1))

        # indicate where the total is, to be used in the next loop
        index_where_total_is = dataframe_table.index[dataframe_table[1] == "Umsatztotal / Schlusssaldo"].tolist()

        # take out the last part
        if index_where_total_is != []:
            dataframe_table_raw = dataframe_table.drop(dataframe_table.index[index_where_total_is[0] + 1:])
        else:
            dataframe_table_raw = dataframe_table

        # select the number of column with witdrawal
        columns_number = dataframe_table.shape[1]
        for column_index in range(columns_number):
            if "Belastung" in dataframe_table.loc[:, column_index].values:
                with_column_index = column_index
            if "Gutschrift" in dataframe_table.loc[:, column_index].values:
                depo_column_index = column_index
            if "Valuta" in dataframe_table.loc[:, column_index].values:
                date_column_index = column_index
            if "Text" in dataframe_table.loc[:, column_index].values:
                text_column_index = column_index
            if "Saldo" in dataframe_table.loc[:, column_index].values:
                balance_column_index = column_index

        # indicate the total of withdrawals and deposits:
        if index_where_total_is != []:
            index = index_where_total_is[0]
            if dataframe_table_raw.loc[index, with_column_index] == '':
                withdrawal_total_decimal = 0.0
            else:
                withdrawal_total_decimal = Decimal(
                    sub(r'[^\d.]', '', dataframe_table_raw.loc[index, with_column_index]))

            if dataframe_table_raw.loc[index, depo_column_index] == '':
                deposit_total_decimal = 0.0
            else:
                deposit_total_decimal = Decimal(sub(r'[^\d.]', '', dataframe_table_raw.loc[index, depo_column_index]))

        # start filling in data
        len_dataframe = dataframe_table_raw.shape[0]
        for row in range(len_dataframe):
            date = dataframe_table_raw.loc[row, date_column_index]
            text = dataframe_table_raw.loc[row, text_column_index]
            if date != '' and date != "Valuta" and text.split()[0] != "Umsatztotal / Schlusssaldo":
                length_date = len(date.split('.'))
                if length_date > 1:
                    year_str = "20" + date.split('.')[2]
                    date_withyear = date.split('.')[0] + " " + date.split('.')[1] + " " + year_str
                    real_month.append(conversion_numeric_month[date.split('.')[1]])
                    real_year.append(year_str)
                    date_withyear_formatted = datetime.datetime.strptime(date_withyear, '%d %m %Y')
                    date_str.append(date_withyear_formatted)

                    # withdrawal and deposit
                    if dataframe_table_raw.loc[row, with_column_index] == '':
                        withdrawal_Decimal.append(Decimal(0.0))
                        withdrawal_boolean.append(False)
                    else:
                        x = dataframe_table_raw.loc[row, balance_column_index].replace("'", "")
                        balance_Decimal.append(x)
                        withdrawal_Decimal.append(
                            Decimal(sub(r'[^\d.]', '', dataframe_table_raw.loc[row, with_column_index])))
                        withdrawal_boolean.append(True)

                    if dataframe_table_raw.loc[row, depo_column_index] == '':
                        deposit_Decimal.append(Decimal(0.0))
                    else:
                        x = dataframe_table_raw.loc[row, balance_column_index].replace("'", "")
                        balance_Decimal.append(x)
                        deposit_Decimal.append(
                            Decimal(sub(r'[^\d.]', '', dataframe_table_raw.loc[row, depo_column_index])))

                    if dataframe_table_raw.loc[row, with_column_index] == '' and dataframe_table_raw.loc[
                        row, depo_column_index] == '':
                        balance_Decimal.append(Decimal(0.0))

                    # accumulate balance if the last value was ''
                    if balance_Decimal[-1] == '':
                        if len(balance_Decimal) > 1:
                            balance_Decimal[-1] = balance_Decimal[-2]
                        else:
                            balance_Decimal[-1] = dataframe_table_raw.loc[row - 1, balance_column_index].replace("'",
                                                                                                                 "")
                            if balance_Decimal[-1] == '':
                                balance_Decimal[-1] = dataframe_table_raw.loc[
                                    row - 2, balance_column_index].replace("'", "")

                    # descriptions
                    description_str.append(dataframe_table_raw.loc[row, text_column_index])

                    if dataframe_table_raw.loc[row + 1, date_column_index] == '':
                        description2_str.append(dataframe_table_raw.loc[row + 1, text_column_index])
                    else:
                        description2_str.append('')

                    try:
                        if dataframe_table_raw.loc[row + 2, date_column_index] == '':
                            description3_str.append(dataframe_table_raw.loc[row + 2, text_column_index])
                        else:
                            description3_str.append('')
                    except:
                        description3_str.append('')

    # category assignment
    category_final2, category1_str, category2_str, category3_str = get_category(description2_str, description3_str,
                                                                                description_str, withdrawal_boolean, CATEGORIES)

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
                                         table_areas=['20,800,700,50'],
                                         columns=['90,300,400,500'])
    dataframe_table_raw = page_table_format[0].df

    # locate where is the name of the account
    index_where_date = 16
    index_where_account = 3
    date = dataframe_table_raw.loc[index_where_date, 2]
    month_str = date.split('. ')[1].split(" ")[0][0:3]
    year_str = date.split(' ')[-1]
    date_statement_str = date.split('.')[0] + " " + month_str + " " + year_str

    account_str = dataframe_table_raw.loc[index_where_account, 1].split(" ")[-1]

    return date_statement_str, month_str, year_str, account_str.replace(" ", "")


def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        elif fullPath.endswith(".pdf"):
            allFiles.append(fullPath)

    return allFiles

# Read pdf into DataFrame
def CS_parser(DIRECTORY, directories):
    registry = pd.DataFrame()
    CATEGORIES, CATEGORIES_DEPOSIT, CATEGORIES_WITHDRAWAL = calc_categories(directories)

    # process data
    # get list folders which indicate the years:
    all_files_paths = getListOfFiles(DIRECTORY)
    registry_accounts = []
    for filepath in all_files_paths:

        # extract account number, balance and month of statement form the first page
        print("Working on file {}".format(filepath.split("/")[-1]))
        date_statement_str, month_str, year_str, account_str = Metadata(filepath)
        registry_accounts.append(account_str)

        print("Working on statement CS {} of the account No. {}".format(date_statement_str, account_str))
        # Iterate over the pages of the statement
        statement_df= Parser_function(filepath, CATEGORIES)

        statement_df["ACCOUNT"] = account_str
        statement_df["STATEMENT"] = date_statement_str
        statement_df["TYPE"] = "CASH"
        statement_df["CURRENCY"] = "CHF"

        registry = pd.concat([registry, statement_df], ignore_index=True)

    registry_accounts = list(set(registry_accounts))
    registry_metadata = pd.DataFrame({"ACCOUNT": registry_accounts,
                                       "TYPE": ["CASH"]*len(registry_accounts),
                                       "CURRENCY": ["CHF"]*len(registry_accounts)})

    return registry, registry_metadata
