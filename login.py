import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from app import app
from apps.menu_page import layout as menu_page_layout
from credentials import USERNAME, PASSWORD
import webbrowser
import os
import json

#import data
file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data_location.json")
with open(file, 'r') as jsonFile:
    data = json.load(jsonFile)

login_page = html.Div(children=[

    # field
    html.H1('The FineBank', style={'text-align': 'center'}),
    html.H4('Please enter details below', style={'text-align': 'center'}),
    html.Br(),
    html.Label('Location and name of database', style={'text-align': 'center'}),
    html.Div([
        dcc.Dropdown(id='login-database', options=[{'label': '/Documents', 'value': 'Documents'},
                                                   {'label': '/Gogle Drive', 'value': 'Google Drive'},
                                                   {'label': '/Downloads', 'value': 'Downloads'}],
                     value=data["location1"])],
        style={'width': '50%', 'float': 'left', 'display': 'inline-block'}),

    html.Div([
        dcc.Input(id='login-database2', type='text', value=data["location2"])],
        style={'width': '50%', 'float': 'right', 'display': 'inline-block'}),

    html.Br(),
    html.Br(),
    html.Br(),
    html.Label('Username', style={'text-align': 'center'}),
    dcc.Input(id='username', placeholder="", type='text', value='', style={'width': '400px'}),
    html.Br(),
    html.Br(),
    html.Label('Password', style={'text-align': 'center'}),
    dcc.Input(id='password', placeholder="", type='password', value='', style={'width': '400px'}),
    # login button
    html.Br(),
    html.Br(),
    html.Button('Login', id='my-button', style={'width': '400px'}),
    html.Br(),
    html.Br(),
    html.Label('(c) Jimeno Fonseca 2019', style={'text-align': 'center'})],
    style={'width': '30%', 'float': 'center', 'display': 'inline-block'},
    )

app.layout = html.Div(id="page", children=[login_page, html.Div(id="dummy"), html.Div(id="dummy2")])


# @app.callback(Output(component_id='dummy', component_property='children'),
#               [Input(component_id='login-database', component_property='value')],
#               )
# def update_database(login_database):
#     file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data_location.json")
#     with open(file, 'r+') as jsonFile2:
#         data2 = json.load(jsonFile2)
#         data2["location1"] = login_database
#         jsonFile.write(json.dumps(data2))
#     return None
#
#
# @app.callback(Output(component_id='dummy2', component_property='children'),
#               [Input(component_id='login-database2', component_property='value')],
#               )
# def update_database2(login_database2):
#
#     return None


@app.callback(Output(component_id='page', component_property='children'),
              [Input(component_id='my-button', component_property='n_clicks')],
              [State(component_id='username', component_property='value'),
               State(component_id='password', component_property='value'),
               State(component_id='login-database', component_property='value'),
               State(component_id='login-database2', component_property='value')]
              )
def change_page(clicks, username, password, location1, location2):
    if (username == USERNAME) and (password == PASSWORD)and clicks is not None:
        data = {"location1": location1, "location2": location2}
        file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data_location.json")
        with open(file, "w") as jsonFile:
            json.dump(data, jsonFile)
        return menu_page_layout
    else:
        return login_page


def main():
    webbrowser.open_new_tab('http://127.0.0.1:8050/')
    app.run_server(debug=False, dev_tools_hot_reload=False,
                   dev_tools_silence_routes_logging=False)


if __name__ == '__main__':
    main()
