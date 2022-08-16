from dash import html, dcc
from apps.layouts import MENU_HTML

layout = html.Div([# Menu on the left
                   MENU_HTML,

                # add piechart of Income
                html.Div([
                    html.Div([html.H2('Income', style={'text-align': 'center'}),
                              dcc.Graph(id='app-1-income')],
                             style={'float': 'left', "margin-top": "10px",
                                    "margin-right": "20px"}
                             ),
                    # add piechart of Expenses
                    html.Div([html.H2('Expenses', style={'text-align': 'center'}),
                              dcc.Graph(id='app-1-expenses')],
                              style={'float': 'left', "margin-top": "10px",
                                     "margin-right": "20px"}),
                    # add piechart of Balance'
                    html.Div([html.H2('Balance', style={'text-align': 'center'}),
                              dcc.Graph(id='app-1-balance')],
                              style={'float': 'left', "margin-top": "10px"}),

                    ], style={'vertical-align': 'top', 'display': 'inline-block', 'float': 'left'}),
                ])

