import dash_daq as daq
from dash import html, dcc


from directories_pointer import directories
from settings import  calc_categories, calc_accounts, calc_years, get_options
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
        dcc.Dropdown(id='app-3-year', options=years_options,
                     value=YEARS_TO_PROCESS[-1], placeholder='Please select a year'),

        html.Br(),
        html.Label('Currency'),
        dcc.RadioItems(id='app-3-currency', options=currencies_options,
                       value='CHF'),
        # add drowpdown menu
        html.Br(),
        html.Label('Cash accounts'),
        dcc.Checklist(id='app-3-accounts', options=cash_accounts_options,
                      value=ACCOUNT_TYPE["CASH"]),

        html.Br(),
        # add my budget line
        html.Label('Budget a month'),
        dcc.Input(id='app-3-my-budget', value=7000, type='number'),

        html.Br(),
        # add my button show budget line
        html.Label('Show my budget line'),
        daq.BooleanSwitch(id='app-3-my-budget-line', on=True),

        # add my button show 3-year average
        html.Label('Show my historical average line'),
        daq.BooleanSwitch(id='app-3-my-historical-average', on=True),

        # add my button show total
        html.Label('Show my total line'),
        daq.BooleanSwitch(id='app-3-my-total', on=True),
    ],
        style={'width': '15%', 'float': 'left', 'display': 'inline-block', 'paddingRight': '20px'}),

    # add barchat of expenses
    html.Div([html.H2('Status'),
              dcc.RadioItems(id='app-3-show-category', options=[{'label': 'Show income', 'value': 'income'},
                                                                {'label': 'Show expenses', 'value': 'expenses'},
                                                                {'label': 'Show balance', 'value': 'balance'},
                                                                {'label': 'Show income spent & savings',
                                                                 'value': 'spent'}
                                                                ],
                             value='balance', labelStyle={'display': 'inline-block', 'padding': '20'}),
              dcc.Graph(id='app-3-status')],
             style={'width': '55%', 'height': '100vh', 'float': 'left', 'display': 'inline-block'}),
    html.Div([html.H2('Status'),
              dcc.Graph(id='app-3-total-last-month')],
             style={'width': '25%', 'display': 'inline-block', 'float': 'right'}),
])
