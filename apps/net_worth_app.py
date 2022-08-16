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
        dcc.Dropdown(id='app-4-year', options=years_options,
                     value=YEARS_TO_PROCESS[-1], placeholder='Please select a year'),
        html.Br(),
        html.Label('Currency'),
        dcc.RadioItems(id='app-4-currency', options=currencies_options,
                       value='CHF'),
        html.Br(),
        html.Label('Cash accounts'),
        dcc.Checklist(id='app-4-cash', options=cash_accounts_options,
                      value=ACCOUNT_TYPE["CASH"]),
        html.Br(),
        # add drowpdown menu
        html.Label('Real Estate'),
        dcc.Checklist(id='app-4-accounts', options=rs_accounts_options,
                      value=ACCOUNT_TYPE["REAL_ESTATE"]),

        html.Br(),
        html.Label('Bonds'),
        dcc.Checklist(id='app-4-bonds',
                      options=bond_accounts_options,
                      value=ACCOUNT_TYPE["BONDS"]),

        html.Br(),
        html.Label('Retirement fund'),
        dcc.Checklist(id='app-4-rfunds', options=retirement_accounts_options,
                      value=ACCOUNT_TYPE["RETIREMENT"]),

    ],
        style={'width': '15%', 'float': 'left', 'display': 'inline-block', 'paddingRight': '20px'}),

    # add barchat of expenses
    html.Div([html.H2('Net Worth'),
              dcc.RadioItems(id='app-4-category-boolean', options=[{'label': 'Show values per category', 'value': True},
                                                                   {'label': 'Show values per account', 'value': False}
                                                                   ],
                             value=True, labelStyle={'display': 'inline-block', 'padding': '20'}),

              dcc.Graph(id='app-4-accumulated-value')],
             style={'width': '55%', 'float': 'left', 'display': 'inline-block'}),
    # add piechart of income
    html.Div([html.H2('Status'),
              dcc.Graph(id='app-4-total-last-month')],
             style={'width': '25%', 'display': 'inline-block', 'float': 'right'}),
])

