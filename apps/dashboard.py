import json

from dash import dcc
from dash import html
import pandas as pd
from dash.dependencies import Input, Output

from application import application as app
from application import tab_style
from apps import overview_app, cash_accounts_app, net_worth_app, investments_app, menu_page
from utils.support_functions import shutdown_server

from directories_pointer import directories
from settings import calc_accounts

directory = directories()
ACCOUNT_TYPE, ACCOUNTS_CURRENCY = calc_accounts(directory)

def query_data():
    directory = directories()
    DATA_PROCESSED_INVESTMENTS = directory["DATA_PROCESSED_INVESTMENTS"]
    DATA_PROCESSED = directory["DATA_PROCESSED_BANKING"]

    # process data
    data_processed_not_pivot = pd.read_csv(DATA_PROCESSED)
    data_processed_investments = pd.read_csv(DATA_PROCESSED_INVESTMENTS)
    data_processed_with_investment = pd.concat([data_processed_not_pivot, data_processed_investments],
                                               ignore_index=True, sort=False)
    data_processed_with_investment = data_processed_with_investment.fillna(0.0)

    # convert date to timeindex
    data_processed_with_investment['DATE'] = pd.to_datetime(data_processed_with_investment['DATE'])

    ##TODO:calculate balance at the end of the month for each account
    data_procesed_end_month_balance = pd.DataFrame()
    for account in ACCOUNTS_CURRENCY.keys():
        dat_balance = data_processed_with_investment[data_processed_with_investment["ACCOUNT"] == account]
        x = dat_balance.groupby([dat_balance['DATE'].dt.year, dat_balance['DATE'].dt.month]).last()
        data_procesed_end_month_balance = data_procesed_end_month_balance.append(x, ignore_index=True, sort=False)

    datasets = {
        'data_processed_with_investment': data_processed_with_investment.to_json(orient='split', date_format='iso'),
        'data_procesed_end_month_balance': data_procesed_end_month_balance.to_json(orient='split',
                                                                                   date_format='iso')}
    return datasets


# select content for the index
header = html.Div([
    html.Div([
        html.Br(),
        dcc.Link('OVERVIEW', href='/apps/overview_app', style=tab_style),
        dcc.Link('CASH ACCOUNTS', href='/apps/cash_accounts_app', style=tab_style),
        dcc.Link('INVESTMENTS', href='/apps/investments_app', style=tab_style),
        dcc.Link('NET-WORTH', href='/apps/net_worth_app', style=tab_style),
        dcc.Link('EXIT', href='/apps/exit', style=tab_style)],
        style={'width': '50%', 'float': 'left', 'display': 'inline-block'}),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
])

layout = html.Div([dcc.Location(id='url', refresh=False),
                   html.Div(id='index_content')])


@app.callback(Output(component_id='index_content', component_property='children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/overview_app':
        return [header, html.Div([json.dumps(query_data())], id='DATABASE', style={'display': 'none'}),
                overview_app.layout]
    elif pathname == '/apps/cash_accounts_app':
        return [header, html.Div([json.dumps(query_data())], id='DATABASE', style={'display': 'none'}),
                cash_accounts_app.layout]
    elif pathname == '/apps/investments_app':
        return [header, html.Div([json.dumps(query_data())], id='DATABASE', style={'display': 'none'}),
                investments_app.layout]
    elif pathname == '/apps/net_worth_app':
        return [header, html.Div([json.dumps(query_data())], id='DATABASE', style={'display': 'none'}),
                net_worth_app.layout]
    elif pathname == '/apps/exit':
        shutdown_server()
        return html.H4("Good Bye!, you can close the browser now", style={'text-align': 'center'})
    else:
        return [header,
                html.Div([json.dumps(query_data())], id='DATABASE', style={'display': 'none'}),
                overview_app.layout]


