import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import numpy as np
from dash.dependencies import Input, Output

from app import app
from graphs import bar_chart_months, pie_chart, pie_chart_last_month
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
                      values=ACCOUNT_TYPE["CASH"]),

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


# update graphs dynamically:

@app.callback(Output(component_id='app-3-status', component_property='figure'),
              [Input(component_id='app-3-year', component_property='value'),
               Input(component_id='app-3-accounts', component_property='values'),
               Input(component_id='app-3-my-budget', component_property='value'),
               Input(component_id='app-3-my-budget-line', component_property='on'),
               Input(component_id='app-3-my-historical-average', component_property='on'),
               Input(component_id='app-3-my-total', component_property='on'),
               Input(component_id='app-3-currency', component_property='value'),
               Input(component_id='app-3-show-category', component_property='value'),
               Input(component_id='DATABASE', component_property='children')]
              )
def app_3_graph_update(year, accounts, budget, show_budget_line, show_3_year_average, show_total, currency, category,
                       data):
    if category == "income":
        return app_3_update_graph_income(year, accounts, show_3_year_average, show_total, currency, data)
    if category == "expenses":
        return app_3_update_graph_expenses(year, accounts, budget, show_budget_line, show_3_year_average, show_total,
                                           currency, data)
    if category == "spent":
        return app_3_update_graph_spent(year, accounts, currency, data)
    if category == "balance":
        return app_3_update_graph_balance(year, accounts, currency, data)


# update graphs dynamically:
@app.callback(Output(component_id='app-3-total-last-month', component_property='figure'),
              [Input(component_id='app-3-year', component_property='value'),
               Input(component_id='app-3-accounts', component_property='values'),
               Input(component_id='app-3-currency', component_property='value'),
               Input(component_id='app-3-show-category', component_property='value'),
               Input(component_id='DATABASE', component_property='children')]
              )
def app_3_graph_pie_update(year, accounts, currency, category, data):
    if category == "income":
        return app_3_update_income_pie(year, accounts, currency, data)
    if category == "expenses":
        return app_3_update_expenses_pie(year, accounts, currency, data)
    if category == "spent":
        return app_3_update_spent_pie(year, accounts, currency, data)
    if category == "balance":
        return app_3_update_balance_pie(year, accounts, currency, data)


def app_3_update_graph_expenses(year, accounts, budget, show_budget_line, show_3_year_average, show_total, currency,
                                data):
    data_processed = get_database("data_processed_with_investment", data[0]).pivot_table(
        index=["YEAR", "MONTH", "ACCOUNT"], columns="CAT",
        aggfunc=np.sum)
    data_frame = data_processed["DEBIT_" + currency]
    data_frame = data_frame.loc[int(year), :, accounts]
    data = data_frame.copy().pivot_table(index=['MONTH'], aggfunc=np.sum)
    analysis_fields_expenses = [x for x in CATEGORIES_WITHDRAWAL if x in data_frame.columns]

    if show_3_year_average:
        historical_data = data_processed.copy()["DEBIT_" + currency]
        check_num_years = historical_data.loc(axis=0)[:, :, accounts]
        m_years = len(set(check_num_years.index.get_level_values(0)))
        historical_data = historical_data.pivot_table(index=['MONTH'], aggfunc=np.sum)
        total = historical_data[analysis_fields_expenses].sum(axis=1) / m_years
    else:
        total = None
    graph = bar_chart_months(data, analysis_fields_expenses, budget=budget, show_budget_line=show_budget_line,
                             show_3_year_average=show_3_year_average,
                             historical_data=total, show_total=show_total)

    return graph


def app_3_update_graph_income(year, accounts, show_3_year_average, show_total, currency, data):
    data_processed = get_database("data_processed_with_investment", data[0]).pivot_table(
        index=["YEAR", "MONTH", "ACCOUNT"], columns="CAT",
        aggfunc=np.sum)
    data_frame = data_processed.copy()["CREDIT_" + currency]
    data_frame = data_frame.loc[int(year), :, accounts]
    data = data_frame.copy().pivot_table(index=['MONTH'], aggfunc=np.sum)
    analysis_fields_income = [x for x in CATEGORIES_DEPOSIT if x in data_frame.columns]

    if show_3_year_average:
        historical_data = data_processed.copy()["CREDIT_" + currency]
        check_num_years = historical_data.loc(axis=0)[:, :, accounts]
        m_years = len(set(check_num_years.index.get_level_values(0)))
        historical_data = historical_data.pivot_table(index=['MONTH'], aggfunc=np.sum)
        total = historical_data[analysis_fields_income].sum(axis=1) / m_years
    else:
        total = None
    graph = bar_chart_months(data, analysis_fields_income, show_3_year_average=show_3_year_average,
                             historical_data=total, show_total=show_total)

    return graph


def app_3_update_graph_spent(year, accounts, currency, data):
    data_processed = get_database("data_processed_with_investment", data[0]).pivot_table(
        index=["YEAR", "MONTH", "ACCOUNT"], columns="CAT",
        aggfunc=np.sum)
    # expenses
    data_frame = data_processed.copy()["DEBIT_" + currency]
    data_frame = data_frame.loc[int(year), :, accounts]
    historical_data_expenses = data_frame.pivot_table(index=['MONTH'], aggfunc=np.sum)
    analysis_fields_expenses = [x for x in CATEGORIES_WITHDRAWAL if x in data_frame.columns]
    historical_data_expenses["Expenses"] = historical_data_expenses[analysis_fields_expenses].sum(axis=1)

    # income
    data_frame = data_processed.copy()["CREDIT_" + currency]
    data_frame = data_frame.loc[int(year), :, accounts]
    historical_data_deposits = data_frame.pivot_table(index=['MONTH'], aggfunc=np.sum)
    analysis_fields_income = [x for x in CATEGORIES_DEPOSIT if x in data_frame.columns]
    historical_data_deposits["Income"] = historical_data_deposits[analysis_fields_income].sum(axis=1)

    # in percentage
    data = historical_data_expenses.join(historical_data_deposits, lsuffix='_x', rsuffix='_y')
    data["Percentage of Income Spent"] = ((data["Expenses"] / data["Income"]) * 100).round(2)
    data["Percentage of Income Saved"] = 100 - data["Percentage of Income Spent"]
    analysis_fields = ["Percentage of Income Spent", "Percentage of Income Saved"]
    graph = bar_chart_months(data, analysis_fields)

    return graph


def app_3_update_graph_balance(year, accounts, currency, data):
    data_processed = get_database("data_procesed_end_month_balance", data[0])
    data_frame = data_processed.pivot_table(index=["YEAR", "MONTH"], columns="ACCOUNT",
                                            values="BALANCE_" + currency, aggfunc=np.mean)
    data_frame = data_frame.fillna(0.0)
    data_frame = data_frame.loc[int(year), :]
    data = data_frame.copy().pivot_table(index=['MONTH'], aggfunc=np.mean)
    analysis_fields = accounts

    graph = bar_chart_months(data, analysis_fields)

    return graph


def app_3_update_spent_pie(year, accounts, currency, data):
    data_processed = get_database("data_processed_with_investment", data[0]).pivot_table(
        index=["YEAR", "MONTH", "ACCOUNT"], columns="CAT",
        aggfunc=np.sum)
    # expenses
    data_frame = data_processed["DEBIT_" + currency]
    data_frame = data_frame.loc[int(year), :, accounts]
    data_frame = data_frame.pivot_table(index=['MONTH'], aggfunc=np.sum)
    data_expenses = data_frame.sum(axis=0)
    analysis_fields_expenses = [x for x in CATEGORIES_WITHDRAWAL if x in data_frame.columns]
    data_expenses['Expenses'] = data_expenses[analysis_fields_expenses].sum()

    # income
    data_frame2 = data_processed["CREDIT_" + currency]
    data_frame2 = data_frame2.loc[int(year), :, accounts]
    data_frame2 = data_frame2.pivot_table(index=['MONTH'], aggfunc=np.sum)
    data_income = data_frame2.sum(axis=0)
    analysis_fields_income = [x for x in CATEGORIES_DEPOSIT if x in data_frame2.columns]
    data_income['Income'] = data_income[analysis_fields_income].sum()

    # get dataframe
    data = data_expenses.append(data_income)
    data["Percentage of Income Spent"] = data["Expenses"].round(2)
    data["Percentage of Income Saved"] = (data["Income"] - data["Expenses"]).round(2)
    analysis_fields = ["Percentage of Income Saved", "Percentage of Income Spent"]
    graph = pie_chart(data, analysis_fields, currency, percentage_flag=True, show_legend=False)

    return graph


def app_3_update_expenses_pie(year, accounts, currency, data):
    data_processed = get_database("data_processed_with_investment", data[0]).pivot_table(
        index=["YEAR", "MONTH", "ACCOUNT"], columns="CAT",
        aggfunc=np.sum)
    data_frame = data_processed["DEBIT_" + currency]
    data_frame = data_frame.loc[int(year), :, accounts]
    data_frame = data_frame.pivot_table(index=['MONTH'], aggfunc=np.sum)
    data = data_frame.sum(axis=0)
    analysis_fields_expenses = [x for x in CATEGORIES_WITHDRAWAL if x in data_frame.columns]
    graph = pie_chart(data, analysis_fields_expenses, currency, show_legend=False)

    return graph


def app_3_update_income_pie(year, accounts, currency, data):
    data_processed = get_database("data_processed_with_investment", data[0]).pivot_table(
        index=["YEAR", "MONTH", "ACCOUNT"], columns="CAT",
        aggfunc=np.sum)
    data_frame = data_processed["CREDIT_" + currency]
    data_frame = data_frame.loc[int(year), :, accounts]
    data_frame = data_frame.pivot_table(index=['MONTH'], aggfunc=np.sum)
    data = data_frame.sum(axis=0)
    analysis_fields_income = [x for x in CATEGORIES_DEPOSIT if x in data_frame.columns]
    graph = pie_chart(data, analysis_fields_income, currency, show_legend=False)

    return graph


def app_3_update_balance_pie(year, accounts, currency, data):
    data_processed = get_database("data_procesed_end_month_balance", data[0])
    data_frame = data_processed.pivot_table(index=["YEAR", "MONTH"], columns="ACCOUNT",
                                            values="BALANCE_" + currency, aggfunc=np.mean)
    data_frame = data_frame.fillna(0.0)
    data_frame = data_frame.loc[int(year), :]
    data = data_frame.copy().pivot_table(index=['MONTH'], aggfunc=np.mean)
    analysis_fields = accounts
    # find the last month in the data displayed
    for month in reversed(MONTH_ORDER):
        if month in data.index:
            last_month = month
            break

    graph = pie_chart_last_month(data, analysis_fields, currency, last_month)

    return graph


if __name__ == '__main__':
    app.run_server(debug=True)
