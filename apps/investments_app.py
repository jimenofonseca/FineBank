from dash import html, dcc

from directories_pointer import directories
from settings import calc_categories, calc_accounts, calc_years, get_options
from colors import calculate_color

directory = directories()
CATEGORIES, CATEGORIES_DEPOSIT, CATEGORIES_WITHDRAWAL = calc_categories(directory)
ACCOUNT_TYPE, ACCOUNTS_CURRENCY = calc_accounts(directory)
YEARS_TO_PROCESS = calc_years(directory)
COLOR = calculate_color(ACCOUNTS_CURRENCY)
years_options, currencies_options, inv_accounts_options, cash_accounts_options, bond_accounts_options, rs_accounts_options, retirement_accounts_options = get_options(YEARS_TO_PROCESS, ACCOUNT_TYPE)

layout = html.Div([
    html.Div([
        html.Label('Year'),
        dcc.Dropdown(id='app-6-year', options=years_options,
                     value=YEARS_TO_PROCESS[-1], placeholder='Please select a year'),

        html.Br(),
        html.Label('Currency'),
        dcc.RadioItems(id='app-6-currency', options=currencies_options,
                       value='CHF'),

        # add drowpdown menu
        html.Br(),
        html.Label('Investment accounts'),
        dcc.RadioItems(id='app-6-accounts', options= inv_accounts_options,
                       value=ACCOUNT_TYPE["REAL_ESTATE"][0]),

    ],
        style={'width': '15%', 'float': 'left', 'display': 'inline-block', 'paddingRight': '20px'}),

    # add barchat of investment
    html.Div([html.H2('Investment'),
              dcc.Graph(id='app-6-investment')],
             style={'width': '55%', 'height': '20vh', 'display': 'inline-block', 'float': 'left'}),

    # add pie of status to data
    html.Div([html.H2('Status'),
              dcc.Graph(id='app-6-real')],
             style={'width': '25%', 'height': '20vh', 'float': 'right', 'display': 'inline-block'}),

])

