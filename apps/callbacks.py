import numpy as np

from application import application as app
from graphs import bar_chart_months, pie_chart, pie_chart_last_month
from settings import MONTH_ORDER
from settings import calc_categories, calc_accounts, calc_years, get_options, calc_type
from utils.support_functions import get_database

from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from directories_pointer import directories
from colors import calculate_color
from apps import menu_page, dashboard
from utils.support_functions import shutdown_server
from investments_parser.parser import main as parser_investments
from statement_parser.parser import main as parser_cash_accounts

directory = directories()
CATEGORIES, CATEGORIES_DEPOSIT, CATEGORIES_WITHDRAWAL = calc_categories(directory)
ACCOUNT_TYPE, ACCOUNTS_CURRENCY = calc_accounts(directory)
YEARS_TO_PROCESS = calc_years(directory)
COLOR = calculate_color(ACCOUNTS_CURRENCY)
years_options, currencies_options, inv_accounts_options, cash_accounts_options, bond_accounts_options, rs_accounts_options, retirement_accounts_options = get_options(YEARS_TO_PROCESS, ACCOUNT_TYPE)

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


@app.callback(Output(component_id='menu_page', component_property='children'),
              [Input(component_id='button_dashboard', component_property='n_clicks')],
              [State(component_id='button_investment', component_property='n_clicks_timestamp'),
               State(component_id='button_accounts', component_property='n_clicks_timestamp'),
               State(component_id='exit_button', component_property='n_clicks_timestamp')]
              )
def change_page_login(clicks_button3, clicks_button1, clicks_button2, clicks_button4):
    if clicks_button3 is not None and (int(clicks_button1) and int(clicks_button2) and int(clicks_button4)) == 0:
        clicks_button3 = None
        return dashboard.layout
    else:
        return [menu_page,
                html.Div(id="status_bar_menu"),
                html.Div(id="status_bar_menu_button_parser_investments"),
                html.Div(id="status_bar_menu_button_parser_cash")]


@app.callback(Output(component_id='status_bar_menu', component_property='children'),
              [Input(component_id='exit_button', component_property='n_clicks')],
              [State(component_id='button_investment', component_property='n_clicks_timestamp'),
               State(component_id='button_accounts', component_property='n_clicks_timestamp'),
               State(component_id='button_dashboard', component_property='n_clicks_timestamp')]
              )
def turn_off(clicks_button3, clicks_button1, clicks_button2, clicks_button4):
    if clicks_button3 is not None and (int(clicks_button1) and int(clicks_button2) and int(clicks_button4)) == 0:
        shutdown_server()
        return html.H4("Good Bye!, you can close the browser now", style={'text-align': 'center'})
    else:
        return None


@app.callback(Output(component_id='status_bar_menu_button_parser_investments', component_property='children'),
              [Input(component_id='button_investment', component_property='n_clicks')],
              [State(component_id='exit_button', component_property='n_clicks_timestamp'),
               State(component_id='button_accounts', component_property='n_clicks_timestamp'),
               State(component_id='button_dashboard', component_property='n_clicks_timestamp')]
              )
def turn_off(clicks_button3, clicks_button1, clicks_button2, clicks_button4):
    if clicks_button3 is not None and (int(clicks_button1) and int(clicks_button2) and int(clicks_button4)) == 0:
        parser_investments()
        return html.H4("Investment data was successfully parsed", style={'text-align': 'center'})
    else:
        return None


@app.callback(Output(component_id='status_bar_menu_button_parser_cash', component_property='children'),
              [Input(component_id='button_accounts', component_property='n_clicks')],
              [State(component_id='exit_button', component_property='n_clicks_timestamp'),
               State(component_id='button_investment', component_property='n_clicks_timestamp'),
               State(component_id='button_dashboard', component_property='n_clicks_timestamp')]
              )
def turn_off(clicks_button3, clicks_button1, clicks_button2, clicks_button4):
    if clicks_button3 is not None and (int(clicks_button1) and int(clicks_button2) and int(clicks_button4)) == 0:
        parser_cash_accounts()
        return html.H4("Bank account data was successfully parsed", style={'text-align': 'center'})
    else:
        return None


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
    if category == "True":
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
    if category == "True":
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


@app.callback(Output(component_id='app-1-placer_menu', component_property='children'),
              [Input(component_id='app-1-show-category', component_property='value')]
              )
def menu(category):
    if category == "True":
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
    if category== "True":
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
    if category == "True":
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
    if category == "True":
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
