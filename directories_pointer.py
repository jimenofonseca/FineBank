import json
import os
import zipfile


def directories():
    # read where the data is
    file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data_location.json")
    with open(file, 'r') as jsonFile:
        data = json.load(jsonFile)
    homedir = os.environ['HOME']
    dir_path = os.path.join(homedir, data["location1"], data["location2"])

    if os.path.isdir(dir_path):
        print('directory found')
        dir_path = dir_path
    else:
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "example_data")


    # directory
    DIRECTORY_DBS = os.path.join(dir_path, "INPUTS", "BANKING", "DBS/")
    DIRECTORY_POSTFINANCE = os.path.join(dir_path, "INPUTS", "BANKING", "POSTFINANCE/")
    DIRECTORY_CREDITSUISSE = os.path.join(dir_path, "INPUTS", "BANKING", "CS/")
    DATA_MANUAL_INPUTS = os.path.join(dir_path, "INPUTS", "BANKING", "_MANUAL", "MANUAL.xlsx")

    DIRECTORY_INVESTMENTS = os.path.join(dir_path, "INPUTS", "INVESTMENTS/")
    DIRECTORY_PROCESSED = os.path.join(dir_path, "OUTPUTS")

    DATA_PROCESSED_INVESTMENTS = os.path.join(DIRECTORY_PROCESSED, "registry_investments.csv")
    DATA_PROCESSED_INVESTMENTS_METADATA = os.path.join(DIRECTORY_PROCESSED, "registry_investments_metadata.csv")

    DATA_PROCESSED_BANKING = os.path.join(DIRECTORY_PROCESSED, "registry_banking.csv")
    DATA_PROCESSED_BANKING_METADATA = os.path.join(DIRECTORY_PROCESSED, "registry_banking_metadata.csv")

    CATEGORIES_DATA = os.path.join(dir_path, "INPUTS", "CATEGORIES.xlsx")

    directories = {"DIRECTORY_DBS": DIRECTORY_DBS,
                   "DIRECTORY_POSTFINANCE": DIRECTORY_POSTFINANCE,
                   "DIRECTORY_CREDITSUISSE": DIRECTORY_CREDITSUISSE,
                   "DATA_MANUAL_INPUTS": DATA_MANUAL_INPUTS,
                   "DIRECTORY_INVESTMENTS": DIRECTORY_INVESTMENTS,
                   "DIRECTORY_PROCESSED": DIRECTORY_PROCESSED,
                   "DATA_PROCESSED_INVESTMENTS": DATA_PROCESSED_INVESTMENTS,
                   "DATA_PROCESSED_INVESTMENTS_METADATA": DATA_PROCESSED_INVESTMENTS_METADATA,
                   "DATA_PROCESSED_BANKING": DATA_PROCESSED_BANKING,
                   "DATA_PROCESSED_BANKING_METADATA": DATA_PROCESSED_BANKING_METADATA,
                   "CATEGORIES_DATA": CATEGORIES_DATA
                   }

    return directories
