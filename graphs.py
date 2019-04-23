from datetime import datetime

import plotly.graph_objs as go
from babel.numbers import format_currency


from settings import MONTH_ORDER
from settings import calc_accounts
from colors import calculate_color
from directories_pointer import directories

directory = directories()
ACCOUNT_TYPE, ACCOUNTS_CURRENCY = calc_accounts(directory)
COLOR = calculate_color(ACCOUNTS_CURRENCY)


def bar_chart_months(new_data_frame, analysis_fields, budget=0.0, show_budget_line=False, show_3_year_average=False,
                     historical_data=None, show_total=False, investment=0.0, legend_font=12):
    # CALCULATE GRAPH
    graph = []
    # check analysis_fields
    analysis_fields2 = [x for x in analysis_fields if x in new_data_frame.columns]

    new_data_frame.loc[:, 'total'] = new_data_frame[analysis_fields2].sum(axis=1)
    for field in analysis_fields2:
        y = new_data_frame[field]
        total_perc = (y / new_data_frame['total'] * 100).round(2).values
        total_perc_txt = ["(" + str(x) + " %)" for x in total_perc]
        trace = go.Bar(x=new_data_frame.index, y=y, name=field, text=total_perc_txt,
                       marker=dict(color=COLOR[field]))
        graph.append(trace)

    if budget > 0.0 and show_budget_line:  # append budget line
        lenghtindex = new_data_frame.shape[0]
        y_line = [int(budget)] * lenghtindex
        trace_line = go.Scatter(x=new_data_frame.index, y=y_line, name="Budget", marker=dict(color="red",
                                                                                             size=12),
                                mode='markers')
        graph.append(trace_line)

    if show_3_year_average:  # append average three year line
        y_line = historical_data
        trace_line = go.Scatter(x=new_data_frame.index, y=y_line, name="Historical", marker=dict(color="orange",
                                                                                                 size=12),
                                mode='markers')
        graph.append(trace_line)

    if show_total:  # append average three year line
        y_line = new_data_frame['total']
        trace_line = go.Scatter(x=new_data_frame.index, y=y_line, name="This year", marker=dict(color="magenta",
                                                                                                size=12),
                                mode='markers')
        graph.append(trace_line)

    if investment > 0.0:  # append budget line
        lenghtindex = new_data_frame.shape[0]
        y_line = [int(investment)] * lenghtindex
        trace_line = go.Scatter(x=new_data_frame.index, y=y_line, name="Initial Investment", marker=dict(color="red",
                                                                                                         size=12),
                                mode='markers')
        graph.append(trace_line)

    layout = go.Layout(barmode='relative',
                       legend=dict(orientation="h", font=dict(size=legend_font)),
                       xaxis=dict(categoryarray=MONTH_ORDER),
                       margin=dict(r=20, t=20, b=10, l=40),
                       hovermode='closest',
                       showlegend=True
                       )

    return {'data': graph, 'layout': layout}


def scatter_chart_months(new_data_frame, field):
    # CALCULATE GRAPH
    graph = []
    # new_data_frame = new_data_frame.reindex(pd.to_datetime(new_data_frame.index, format='%b'))
    # new_data_frame.sort_index(axis=0, inplace=True)
    # print(new_data_frame)
    y = new_data_frame[field]
    trace = go.Scatter(x=new_data_frame.index, y=y, name=field,
                       marker=dict(color=COLOR[field]))
    graph.append(trace)
    layout = go.Layout(legend=dict(orientation="h"),
                       xaxis=dict(categoryarray=MONTH_ORDER),
                       margin=dict(r=20, t=20, b=10, l=40),
                       hovermode='closest',
                       showlegend=True
                       )

    return {'data': graph, 'layout': layout}


def pie_chart(new_data_frame, analysis_fields, currency, percentage_flag=False, show_legend=True):
    # CALCULATE GRAPH
    graph = []
    data_final = new_data_frame[analysis_fields]
    colors = [COLOR[field] for field in analysis_fields]
    total = data_final.copy().sum()
    total_perc = (data_final / total * 100).round(2)
    total_perc_txt = ["(" + str(x) + " %)" for x in total_perc]
    trace = go.Pie(labels=data_final.index, values=data_final[analysis_fields], text=total_perc_txt,
                   hole=.7, hoverinfo="label+value+text", textposition='inside', marker=dict(colors=colors)
                   )

    if percentage_flag:
        central_text = str(((new_data_frame["Expenses"] / new_data_frame["Income"]) * 100).round(2)) + "%"
    else:
        central_text = format_currency(total, currency, locale='en_US')
    layout = go.Layout(showlegend=show_legend,
                       legend=dict(orientation="h",
                                   xanchor="center",
                                   x=0.5),
                       margin=dict(r=10, t=30, b=30, l=10),
                       hovermode='closest',
                       annotations=[dict(text=central_text,
                                         showarrow=False,
                                         font=dict(
                                             size=20
                                         ))])

    return {'data': [trace], 'layout': layout}


def pie_chart_last_month(new_data_frame, analysis_fields, currency, last_month, show_legend=False, show_interest=False,
                         get_initial_investment_year=False, get_initial_investment_month=False, year=False):
    # CALCULATE GRAPH
    graph = []
    data_final = new_data_frame.loc[last_month, analysis_fields]
    colors = [COLOR[field] for field in analysis_fields]
    total = (data_final.sum()).round(2)
    total_perc = (data_final / total * 100).round(2)
    total_perc_txt = ["(" + str(x) + " %)" for x in total_perc]

    if show_interest:
        date_today = datetime.strptime("01 " + last_month + " " + str(year), '%d %b %Y')
        date_investment = datetime.strptime(
            "01 " + get_initial_investment_month + " " + str(get_initial_investment_year), '%d %b %Y')
        dif_months = diff_month(date_today, date_investment)
        interests = (data_final['Interests earned to date'] / data_final['Initial investment']) * 100
        investments_out = new_data_frame.loc[last_month, ['Investments out']]
        text_intermediate = "VALUE: " + format_currency((total - investments_out[0]), currency, locale='en_US')
        central_text = "IRR: " + str(((interests / dif_months) * 12).round(2)) + " %"
    else:
        central_text = format_currency(total, currency, locale='en_US')
        text_intermediate = ""

    trace = go.Pie(labels=data_final.index, values=data_final[analysis_fields], text=total_perc_txt,
                   hole=.7, hoverinfo="label+value+text", textposition='inside', marker=dict(colors=colors)
                   )

    layout = go.Layout(showlegend=show_legend,
                       title=text_intermediate,
                       legend=dict(orientation="h"),
                       margin=dict(r=10, t=30, b=30, l=10),
                       hovermode='closest',
                       annotations=[dict(text=central_text,
                                         showarrow=False,
                                         font=dict(
                                             size=20
                                         ))])

    return {'data': [trace], 'layout': layout}


def pie_chart_IRR(new_data_frame, analysis_fields, currency, last_month, show_legend=False, show_interest=False,
                  get_initial_investment_year=False, get_initial_investment_month=False, year=False):
    # CALCULATE GRAPH
    graph = []
    data_final = new_data_frame.loc[last_month, analysis_fields]
    colors = [COLOR[field] for field in analysis_fields]
    total = (data_final.sum()).round(2)
    total_perc = (data_final / total * 100).round(2)
    total_perc_txt = ["(" + str(x) + " %)" for x in total_perc]

    if show_interest:
        date_today = datetime.strptime("01 " + last_month + " " + str(year), '%d %b %Y')
        date_investment = datetime.strptime(
            "01 " + get_initial_investment_month[0] + " " + str(get_initial_investment_year[0]), '%d %b %Y')
        dif_months = diff_month(date_today, date_investment)
        interests = (data_final['Interests earned to date'] / data_final['Initial investment']) * 100
        investments_out = new_data_frame.loc[last_month, ['Investments out']]
        text_intermediate = "VALUE: " + format_currency((total - investments_out[0]), currency, locale='en_US')
        central_text = "IRR: " + str(((interests / dif_months) * 12).round(2)) + " %"
    else:
        central_text = format_currency(total, currency, locale='en_US')
        text_intermediate = ""

    trace = go.Pie(labels=data_final.index, values=data_final[analysis_fields], text=total_perc_txt,
                   hole=.7, hoverinfo="label+value+text", textposition='inside', marker=dict(colors=colors)
                   )

    layout = go.Layout(showlegend=show_legend,
                       title=text_intermediate,
                       legend=dict(orientation="h"),
                       margin=dict(r=10, t=30, b=30, l=10),
                       hovermode='closest',
                       annotations=[dict(text=central_text,
                                         showarrow=False,
                                         font=dict(
                                             size=20
                                         ))])

    return {'data': [trace], 'layout': layout}


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month
