import dash


application = dash.Dash(__name__, suppress_callback_exceptions=True)
server = application.server
application.scripts.config.serve_locally = True
application.css.config.serve_locally = True

tab_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'borderLeft': '1px solid #d6d6d6',
    'borderRight': '1px solid #d6d6d6',
    'padding': '20px',
    'height': '100px',
    "text-decoration": "none"
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'borderLeft': '1px solid #d6d6d6',
    'borderRight': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '20x',
    'height': '100px',
    "text-decoration": "none"
}