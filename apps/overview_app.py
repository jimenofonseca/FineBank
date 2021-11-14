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
        html.Label('Type'),
        dcc.RadioItems(id='app-1-show-category', options=[{'label': 'Show year', 'value': "True"},
                                                          {'label': 'Show year to year', 'value': "False"}],
                       value=True),
        html.Br(),
        html.Label('Year'),
        html.Div(id='app-1-placer_menu', children=[dcc.Dropdown(id='app-1-year', options=years_options,
                                                                value=YEARS_TO_PROCESS[-1],
                                                                placeholder='Please select a year')]),

        html.Br(),
        html.Label('Currency'),
        dcc.RadioItems(id='app-1-currency', options=currencies_options,
                       value='CHF'),
        html.Br(),
    ],
        style={'width': '15%', 'float': 'left', 'display': 'inline-block', 'paddingRight': '20px'}),

    # add piechart of balanc
    html.Div([html.H2('Net-worth', style={'text-align': 'center'}),
              dcc.Graph(id='app-1-net-worth')],
             style={'width': '27%', 'display': 'inline-block', 'float': 'left', }),
    # add piechart of expenses year
    html.Div([html.H2('Expenses', style={'text-align': 'center'}),
              dcc.Graph(id='app-1-expenses-per-year', style={'height': '73vh', })],
             style={'width': '27%', 'height': '100vh', 'display': 'inline-block', 'float': 'center', }),
    # add piechart of income
    html.Div([html.H2('Income', style={'text-align': 'center'}),
              dcc.Graph(id='app-1-income-per-year')],
             style={'width': '27%', 'display': 'inline-block', 'float': 'right', }),

])

