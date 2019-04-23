import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from settings import MONTH_ORDER
from graphs import pie_chart, pie_chart_last_month, bar_chart_months
import numpy as np
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


@app.callback(Output(component_id='app-1-placer_menu', component_property='children'),
              [Input(component_id='app-1-show-category', component_property='value')]
              )
def menu(category):
    if category:
        return [dcc.Dropdown(id='app-1-year', options=years_options,
                             value=YEARS_TO_PROCESS[-1], placeholder='Please select a year')]
    else:
        return [dcc.Dropdown(id='app-1-year', options=years_options,
                             value=YEARS_TO_PROCESS, multi=True, placeholder='Please select a year')]


@app.callback(Output(component_id='app-1-net-worth', component_property='figure'),
              [Input(component_id='app-1-year', component_property='value'),
               Input(component_id='app-1-currency', component_property='value'),
               Input(component_id='app-1-show-category', component_property='value'),
               Input(component_id='DATABASE', component_property='children')]
              )
def update_net_worth(year, currency, category, data):
    data_procesed_end_month_balance = get_database("data_procesed_end_month_balance", data[0])
    if category:
        data_processed_2 = data_procesed_end_month_balance.copy()
        data_processed_2["TYPE"] = data_processed_2["ACCOUNT"].apply(lambda x: calc_type(x, ACCOUNT_TYPE))
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

        graph = pie_chart_last_month(data, analysis_fields, currency, last_month, show_legend=True)
    else:
        years = [int(x) for x in year]
        data_processed_3 = data_procesed_end_month_balance.copy()
        data_processed_3["TYPE"] = data_processed_3["ACCOUNT"].apply(lambda x: calc_type(x, ACCOUNT_TYPE))
        data_frame = data_processed_3.pivot_table(index=["YEAR", "MONTH", "ACCOUNT"], columns="TYPE",
                                                  values="BALANCE_" + currency, aggfunc=np.mean)
        data_frame = data_frame.fillna(0.0)
        data_frame = data_frame.loc[years, "Dec", :]
        data = data_frame.copy().pivot_table(index=['YEAR'], aggfunc=np.sum)

        analysis_fields = ACCOUNT_TYPE.keys()

        graph = bar_chart_months(data, analysis_fields)

    return graph


@app.callback(Output(component_id='app-1-expenses-per-year', component_property='figure'),
              [Input(component_id='app-1-year', component_property='value'),
               Input(component_id='app-1-currency', component_property='value'),
               Input(component_id='app-1-show-category', component_property='value'),
               Input(component_id='DATABASE', component_property='children')]
              )
def update_graph_expenses_pie(year, currency, category, data):
    data_processed_with_investment = get_database("data_processed_with_investment", data[0])
    data_frame = data_processed_with_investment.pivot_table(index=["YEAR", "MONTH", "ACCOUNT"], columns="CAT",
                                                                   aggfunc=np.sum)["DEBIT_" + currency]
    if category:
        data_frame = data_frame.loc[int(year), :, :]
        data_frame = data_frame.pivot_table(index=['MONTH'], aggfunc=np.sum)
        data = data_frame.sum(axis=0)
        analysis_fields_expenses = [x for x in CATEGORIES_WITHDRAWAL if x in data_frame.columns]
        graph = pie_chart(data, analysis_fields_expenses, currency)
    else:
        years = [int(x) for x in year]
        data_frame = data_frame.loc[years, :, :]
        data_frame = data_frame.pivot_table(index=['YEAR'], aggfunc=np.sum)
        analysis_fields_expenses = [x for x in CATEGORIES_WITHDRAWAL if x in data_frame.columns]

        graph = bar_chart_months(data_frame, analysis_fields_expenses, legend_font=8)

    return graph


@app.callback(Output(component_id='app-1-income-per-year', component_property='figure'),
              [Input(component_id='app-1-year', component_property='value'),
               Input(component_id='app-1-currency', component_property='value'),
               Input(component_id='app-1-show-category', component_property='value'),
               Input(component_id='DATABASE', component_property='children')]
              )
def update_graph_income_pie(year, currency, category, data):
    data_processed_with_investment = get_database("data_processed_with_investment", data[0])
    data_frame = data_processed_with_investment.copy().pivot_table(index=["YEAR", "MONTH", "ACCOUNT"], columns="CAT",
                                                                   aggfunc=np.sum)["CREDIT_" + currency]
    if category:
        data_frame = data_frame.loc[int(year), :, :]
        data_frame = data_frame.pivot_table(index=['MONTH'], aggfunc=np.sum)
        data = data_frame.sum(axis=0)
        analysis_fields_income = [x for x in CATEGORIES_DEPOSIT if x in data_frame.columns]
        graph = pie_chart(data, analysis_fields_income, currency)
    else:
        years = [int(x) for x in year]
        data_frame = data_frame.loc[years, :, :]
        data_frame = data_frame.pivot_table(index=['YEAR'], aggfunc=np.sum)
        analysis_fields_expenses = [x for x in CATEGORIES_DEPOSIT if x in data_frame.columns]

        graph = bar_chart_months(data_frame, analysis_fields_expenses)

    return graph
