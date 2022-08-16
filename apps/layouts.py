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

MENU_HTML = html.Div([
                        html.Label('Type'),
                        dcc.RadioItems(id='app-1-show-category', options=[{'label': 'Show year', 'value': True},
                                                                          {'label': 'Show year to year', 'value': False}],
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
                        style={'width': '200px', 'float': 'left', 'display': 'inline-block', 'paddingRight': '20px'})