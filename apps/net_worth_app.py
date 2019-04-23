import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from settings import MONTH_ORDER
from graphs import bar_chart_months, pie_chart_last_month
import numpy as np
from settings import calc_type
from app import app
from utils.support_functions import get_database

from directories_pointer import directories
from settings import calc_type, calc_categories, calc_accounts, calc_years, get_options
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
                      values=ACCOUNT_TYPE["CASH"]),
        html.Br(),
        # add drowpdown menu
        html.Label('Real Estate'),
        dcc.Checklist(id='app-4-accounts', options=rs_accounts_options,
                      values=ACCOUNT_TYPE["REAL_ESTATE"]),

        html.Br(),
        html.Label('Bonds'),
        dcc.Checklist(id='app-4-bonds',
                      options=bond_accounts_options,
                      values=ACCOUNT_TYPE["BONDS"]),

        html.Br(),
        html.Label('Retirement fund'),
        dcc.Checklist(id='app-4-rfunds', options=retirement_accounts_options,
                      values=ACCOUNT_TYPE["RETIREMENT"]),

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


# update graphs dynamically:

@app.callback(Output(component_id='app-4-accumulated-value', component_property='figure'),
              [Input(component_id='app-4-year', component_property='value'),
               Input(component_id='app-4-accounts', component_property='values'),
               Input(component_id='app-4-bonds', component_property='values'),
               Input(component_id='app-4-rfunds', component_property='values'),
               Input(component_id='app-4-cash', component_property='values'),
               Input(component_id='app-4-currency', component_property='value'),
               Input(component_id='app-4-category-boolean', component_property='value'),
               Input(component_id='DATABASE', component_property='children')]
              )
def update_graph_monthly_values(year, accounts, bonds, rfunds, cash, currency, category, data):
    data_processed= get_database("data_procesed_end_month_balance", data[0])
    if category:
        data_processed_2 = data_processed.loc[data_processed["ACCOUNT"].isin(accounts + bonds + rfunds + cash)]
        data_processed_2.loc[:, "TYPE"] = data_processed_2["ACCOUNT"].apply(lambda x: calc_type(x, ACCOUNT_TYPE))
        data_frame = data_processed_2.pivot_table(index=["YEAR", "MONTH", "ACCOUNT"], columns="TYPE",
                                                  values="BALANCE_" + currency, aggfunc=np.mean)
        data_frame = data_frame.fillna(0.0)
        data_frame = data_frame.loc[int(year), :, :]
        data = data_frame.copy().pivot_table(index=['MONTH'], aggfunc=np.sum)
        analysis_fields = ACCOUNT_TYPE.keys()

        graph = bar_chart_months(data, analysis_fields)

    else:
        data_frame = data_processed.pivot_table(index=["YEAR", "MONTH"], columns="ACCOUNT",
                                                values="BALANCE_" + currency, aggfunc=np.mean)
        data_frame = data_frame.fillna(0.0)
        data_frame = data_frame.loc[int(year), :]
        data = data_frame.copy().pivot_table(index=['MONTH'], aggfunc=np.mean)
        analysis_fields = accounts + bonds + rfunds + cash

        graph = bar_chart_months(data, analysis_fields)

    return graph


@app.callback(Output(component_id='app-4-total-last-month', component_property='figure'),
              [Input(component_id='app-4-year', component_property='value'),
               Input(component_id='app-4-accounts', component_property='values'),
               Input(component_id='app-4-bonds', component_property='values'),
               Input(component_id='app-4-rfunds', component_property='values'),
               Input(component_id='app-4-cash', component_property='values'),
               Input(component_id='app-4-currency', component_property='value'),
               Input(component_id='app-4-category-boolean', component_property='value'),
               Input(component_id='DATABASE', component_property='children')]
              )
def update_graph_income_pie(year, accounts, bonds, rfunds, cash, currency, category, data):
    data_processed = get_database("data_procesed_end_month_balance", data[0])
    if category:
        data_processed_2 = data_processed.loc[data_processed["ACCOUNT"].isin(accounts + bonds + rfunds + cash)]
        data_processed_2.loc[:, "TYPE"] = data_processed_2["ACCOUNT"].apply(lambda x: calc_type(x, ACCOUNT_TYPE))
        data_frame = data_processed_2.pivot_table(index=["YEAR", "MONTH", "ACCOUNT"], columns="TYPE",
                                                  values="BALANCE_" + currency, aggfunc=np.mean)
        data_frame = data_frame.fillna(0.0)
        data_frame = data_frame.loc[int(year), :, :]
        data = data_frame.copy().pivot_table(index=['MONTH'], aggfunc=np.sum)
        analysis_fields = ACCOUNT_TYPE.keys()

        # find the last month in the data displayed
        for month in reversed(MONTH_ORDER):
            if month in data.index:
                last_month = month
                break

        graph = pie_chart_last_month(data, analysis_fields, currency, last_month)

    else:
        data_frame = data_processed.pivot_table(index=["YEAR", "MONTH"], columns="ACCOUNT",
                                                values="BALANCE_" + currency, aggfunc=np.mean)
        data_frame = data_frame.fillna(0.0)
        data_frame = data_frame.loc[int(year), :]
        data = data_frame.copy().pivot_table(index=['MONTH'], aggfunc=np.mean)
        analysis_fields = accounts + bonds + rfunds + cash

        # find the last month in the data displayed
        for month in reversed(MONTH_ORDER):
            if month in data.index:
                last_month = month
                break

        graph = pie_chart_last_month(data, analysis_fields, currency, last_month)

    return graph

