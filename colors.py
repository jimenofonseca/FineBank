import random
# GET COLORS OF CEA
COLORS_TO_RGB = {"red": "rgb(240,75,91)",
                 "red_light": "rgb(246,148,143)",
                 "red_lighter": "rgb(252,217,210)",
                 "blue": "rgb(63,192,194)",
                 "blue_light": "rgb(171,221,222)",
                 "blue_lighter": "rgb(225,242,242)",
                 "yellow": "rgb(255,209,29)",
                 "yellow_light": "rgb(255,225,133)",
                 "yellow_lighter": "rgb(255,243,211)",
                 "brown": "rgb(174,148,72)",
                 "brown_light": "rgb(201,183,135)",
                 "brown_lighter": "rgb(233,225,207)",
                 "purple": "rgb(171,95,127)",
                 "purple_light": "rgb(198,149,167)",
                 "purple_lighter": "rgb(231,214,219)",
                 "green": "rgb(126,199,143)",
                 "green_light": "rgb(178,219,183)",
                 "green_lighter": "rgb(227,241,228)",
                 "grey": "rgb(68,76,83)",
                 "grey_light": "rgb(126,127,132)",
                 "black": "rgb(35,31,32)",
                 "white": "rgb(255,255,255)",
                 "orange": "rgb(245,131,69)",
                 "orange_light": "rgb(248,159,109)",
                 "orange_lighter": "rgb(254,220,198)"}

COLOR_CATEGORY = {'Salary': "yellow",
                  'Percentage of Income Spent': "blue",
                  'Percentage of Income Saved': "blue_light",
                  'Expenses': "blue_light",
                  'Positive Interest': "yellow_light",
                  "Unknown Deposit": "grey_light",
                  "Investments": "yellow",
                  "Public transport": "green_light",
                  'Apartment': "purple",
                  'Bills': "orange",
                  'Taxi': "green",
                  'Gym': "red_light",
                  'Supermarket': "brown_light",
                  'Health': "brown",
                  'Trips': "red",
                  'Restaurant': "purple_light",
                  "Unknown Withdrawal": "grey",
                  'Taxes': "orange_light",
                  "Rent Earnings": "red_light",
                  "JF-PUBLICA": "red",
                  "LF-PUBLICA": "red_light",
                  "APT501": "blue_lighter",
                  "LAX": "blue",
                  "NIDAU": "blue_light",
                  'CDT-212960': "green",
                  'CDT-211160': 'green_light',
                  'CDT-214370': 'green_lighter',
                  '120-045453-0': "orange",
                  '063-015834-8': "orange_light",
                  '92-785858-6': 'yellow',
                  '31-296964-2': 'yellow_light',
                  "REAL_ESTATE": "blue",
                  "BONDS": "green",
                  "RETIREMENT": "red",
                  "CASH": "yellow",
                  "Initial investment": "red",
                  "Interests earned to date": "yellow",
                  "Interest Earned": "yellow_light",
                  "O&M Real Estate": "black"}


def calculate_color(ACCOUNTS_CURRENCY):
    dictionary = {cat: COLORS_TO_RGB[color] for cat, color in COLOR_CATEGORY.items()}
    for account in ACCOUNTS_CURRENCY.keys():
        if account not in dictionary.keys():
            dictionary.update({account: random.choice(list(COLORS_TO_RGB.values()))})
    return dictionary

if __name__ == '__main__':
    x = 1
