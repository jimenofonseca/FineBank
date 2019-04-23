import dash_html_components as html
from dash.dependencies import Input, Output, State
from app import app
from apps import index
from utils.support_functions import shutdown_server
from investments_parser.parser import main as parser_investments
from statement_parser.parser import main as parser_cash_accounts
import importlib

menu_page = html.Div(children=[

    # field
    html.H1('The FineBank', style={'text-align': 'center'}),
    html.H4('Please select an option', style={'text-align': 'center'}),
    # login button
    html.Br(),
    html.Button('Parse Investments', id='button_investment', n_clicks_timestamp='0', style={'width': '400px'}),
    # login button
    html.Br(),
    html.Br(),
    html.Button('Parse Cash accounts', id='button_accounts', n_clicks_timestamp='0', style={'width': '400px'}),
    # login button
    html.Br(),
    html.Br(),
    html.Button('Run the dashboard', id='button_dashboard', n_clicks_timestamp='0', style={'width': '400px'}),
    # exit button
    html.Br(),
    html.Br(),
    html.Button('EXIT', id='exit_button', n_clicks_timestamp='0', style={'width': '400px'}),
    html.Br(),
    html.Br(),
    html.Label('(c) Jimeno Fonseca 2019', style={'text-align': 'center'})
],
    style={'width': '30%', 'float': 'left', 'display': 'inline-block'})

layout = html.Div(id="menu_page", children=[menu_page])


@app.callback(Output(component_id='menu_page', component_property='children'),
              [Input(component_id='button_dashboard', component_property='n_clicks')],
              [State(component_id='button_investment', component_property='n_clicks_timestamp'),
               State(component_id='button_accounts', component_property='n_clicks_timestamp'),
               State(component_id='exit_button', component_property='n_clicks_timestamp')]
              )
def change_page_login(clicks_button3, clicks_button1, clicks_button2, clicks_button4):
    if clicks_button3 is not None and (int(clicks_button1) and int(clicks_button2) and int(clicks_button4)) == 0:
        clicks_button3 = None
        return index.layout
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
