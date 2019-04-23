import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from dash.dependencies import Input, Output

from app import app
from graphs import bar_chart_months, pie_chart_last_month
from settings import MONTH_ORDER
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


# update graphs dynamically:
@app.callback(Output('app-6-accounts', 'options'),
                [Input(component_id='app-6-year', component_property='value'),
                 Input(component_id='DATABASE', component_property='children')
                 ])
def update_options(selected_year, data):
    data_processed = get_database("data_processed_with_investment", data[0])
    existing_accounts = []
    for x in inv_accounts_options:
        account = list(x.values())[1]
        get_data_account = data_processed.loc[data_processed["ACCOUNT"] == account]
        if int(selected_year) in get_data_account["YEAR"].values:
            existing_accounts.append({"label":account, "value":account})
    return existing_accounts

@app.callback(Output('app-6-accounts', 'value'),
                [Input('app-6-accounts', 'options')])
def update_values(options):
    return list(options[0].values())[1]


@app.callback(Output(component_id='app-6-investment', component_property='figure'),
              [Input(component_id='app-6-year', component_property='value'),
               Input(component_id='app-6-accounts', component_property='value'),
               Input(component_id='app-6-currency', component_property='value'),
               Input(component_id='DATABASE', component_property='children')]
              )
def update_graph_barchart(year, account, currency, data):
    data_processed = get_database("data_processed_with_investment", data[0])
    # classify per account
    get_initial_investment = data_processed.loc[data_processed["ACCOUNT"] == account]
    get_initial_investment = get_initial_investment.loc[get_initial_investment["CAT"] == "Initial Investment"]
    get_initial_investment = get_initial_investment.sum(axis=0)
    get_initial_investment = get_initial_investment["CREDIT_" + currency]

    # get balance end of the month
    data_processed2 = get_database("data_procesed_end_month_balance", data[0])
    data_frame = data_processed2.pivot_table(index=["YEAR", "MONTH"], columns="ACCOUNT",
                                             values="BALANCE_" + currency, aggfunc=np.mean)
    data_frame = data_frame.fillna(0.0)
    data_frame = data_frame.loc[int(year), :]
    data = data_frame.copy().pivot_table(index=['MONTH'], aggfunc=np.mean)
    analysis_fields = [account]

    graph = bar_chart_months(data, analysis_fields, investment=get_initial_investment)

    return graph


@app.callback(Output(component_id='app-6-real', component_property='figure'),
              [Input(component_id='app-6-year', component_property='value'),
               Input(component_id='app-6-accounts', component_property='value'),
               Input(component_id='app-6-currency', component_property='value'),
               Input(component_id='DATABASE', component_property='children')]
              )
def update_graph_pie(year, account, currency, data):
    data_processed = get_database("data_processed_with_investment", data[0])
    get_initial_investment = data_processed.loc[data_processed["ACCOUNT"] == account]
    get_initial_investment = get_initial_investment.loc[get_initial_investment["CAT"] == "Initial Investment"]

    get_initial_investment_year = get_initial_investment["YEAR"].values
    get_initial_investment_month = get_initial_investment["MONTH"].values

    if get_initial_investment.shape[0] > 1:  # there two values
        get_initial_investment = get_initial_investment["CREDIT_" + currency].sum()
        get_initial_investment_year = get_initial_investment_year[0]
        get_initial_investment_month = get_initial_investment_month[0]
    else:
        get_initial_investment = get_initial_investment["CREDIT_" + currency].values[0]
        get_initial_investment_year = get_initial_investment_year[0]
        get_initial_investment_month = get_initial_investment_month[0]

    data_processed2 = get_database("data_procesed_end_month_balance", data[0])
    data_frame = data_processed2.pivot_table(index=["YEAR", "MONTH"], columns="ACCOUNT",
                                             values="BALANCE_" + currency, aggfunc=np.mean)
    data_frame = data_frame.fillna(0.0)
    data_frame = data_frame.loc[int(year), :]
    data = data_frame.copy().pivot_table(index=['MONTH'], aggfunc=np.mean)
    analysis_fields = ["Initial investment", 'Interests earned to date']

    # disocunt any investment out of the main investment for instance colimbian apartment ot pay other bonds
    data_invetments_out = data_processed.loc[data_processed["ACCOUNT"] == account]
    data_invetments_out = data_invetments_out.loc[data_invetments_out["CAT"] == "Investments"]
    data_invetments_out = data_invetments_out.sum(0)
    data_invetments_out = data_invetments_out["DEBIT_" + currency]

    # calculate total interest earned to date and initial investment
    data['Interests earned to date'] = data[account] - get_initial_investment + data_invetments_out
    data['Investments out'] = data_invetments_out
    data["Initial investment"] = get_initial_investment

    # find the last month in the data displayed
    for month in reversed(MONTH_ORDER):
        if month in data.index:
            last_month = month
            break

    graph = pie_chart_last_month(data, analysis_fields, currency, last_month, show_legend=True, show_interest=True,
                                 get_initial_investment_year=get_initial_investment_year,
                                 get_initial_investment_month=get_initial_investment_month,
                                 year=int(year))

    return graph
