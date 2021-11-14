from dash import html


menu_page = html.Div(children=[

    # field
    html.H1('The FineBank', style={'text-align': 'center'}),
    html.H4('Please select an option', style={'text-align': 'center'}),
    # login button
    html.Br(),
    html.Button('Parse Investments', id='button_investment', n_clicks_timestamp=0, style={'width': '400px'}),
    # login button
    html.Br(),
    html.Br(),
    html.Button('Parse Cash accounts', id='button_accounts', n_clicks_timestamp=0, style={'width': '400px'}),
    # login button
    html.Br(),
    html.Br(),
    html.Button('Run the dashboard', id='button_dashboard', n_clicks_timestamp=0, style={'width': '400px'}),
    # exit button
    html.Br(),
    html.Br(),
    html.Button('EXIT', id='exit_button', n_clicks_timestamp=0, style={'width': '400px'}),
    html.Br(),
    html.Br(),
    html.Label('(c) Jimeno Fonseca 2019', style={'text-align': 'center'})
],
    style={'width': '30%', 'float': 'left', 'display': 'inline-block'})

layout = html.Div(id="menu_page",
                  children=[menu_page])

