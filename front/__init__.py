import dash
import requests
import numpy as np
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from datetime import datetime
from dash import dcc, html, Input, Output


def get_index(array, value):
    return np.argmin(np.abs(array - value))


def get_range(array, value):
    range_values = (min(array) - max(abs(array))*value,
                    max(array) + max(abs(array))*value)
    return range_values


def str_to_datetime(array):
    new_array = []
    for i in array:
        new_array.append(datetime.strptime(i, '%d.%m.20%y %H-%M-%S'))
    return new_array


colors = ['jet', 'inferno', 'magenta', 'turbo', 'portland']
color_list_box = dcc.Dropdown(colors, colors[-1], id='color-list-box')
matrix_list_box = dcc.Dropdown(['heatmap', 'contour'], 'heatmap', id='matrix-list-box')


def create_layout(depth, times):
    depth_slider = dcc.Slider(
        id='md-slider',
        max=min(depth) * -1,
        min=max(depth) * -1,
        value=min(depth) * -1,
        vertical=True,
        verticalHeight=470,
        included=False,
        tooltip={'placement': 'left', 'always_visible': True}
    )

    time_slider = dcc.Slider(
        id='time-slider',
        min=min(times).timestamp(),
        max=max(times).timestamp(),
        marks={
            int(min(times).timestamp()): min(times).time(),
            int(max(times).timestamp()): max(times).time(),
        },
        value=max(times).timestamp(),
        included=False,
    )

    result_layout = html.Div([

        dbc.Row(html.H1('DTS Monitor'), style={'margin-bottom': '10px', 'margin-top': '10px'}),

        dbc.Row([

            dbc.Col([
                html.Div('MD slider',
                         style={'text-align': 'left', 'margin-left': '5px', 'width': '100px'}),
                html.Div(depth_slider, style={'margin-top': '12px'})
            ], width=1),

            dbc.Col([
                dcc.Graph(id='matrix',
                          style={'height': '538px', 'width': '100%', 'margin-left': '10px'}),  # 'width': '800px'
                html.Div('Time slider',
                         style={'text-align': 'left', 'margin-left': '5px'}),
                html.Div(time_slider,
                         style={'margin-left': '30px', 'width': '100%'}),  # 'width': '720px'
                dcc.Graph(id='time-line', style={'height': '220px'})
            ], width=8),

            dbc.Col([
                html.Div('MD graph', style={'margin-left': '40px'}),
                dcc.Graph(id='md-line', style={'height': '500px'}),
                html.Div('Current colorscale', style={'margin-top': '20px', 'margin-left': '40px'}),
                html.Div(color_list_box, style={'margin-top': '5px', 'margin-left': '40px'}),
                html.Div('Current matrix type', style={'margin-top': '20px', 'margin-left': '40px'}),
                html.Div(matrix_list_box, style={'margin-top': '5px', 'margin-left': '40px'}),
                dcc.Interval(id='interval-data', interval=10*1000, n_intervals=0),  # interval in ms
                dcc.Interval(id='interval-draw', interval=1*1000, n_intervals=0),
                html.Div(id='hidden-div', style={'display': 'none'}),
            ], width=3)
        ])
    ], style={'margin-left': '100px', 'margin-right': '100px'})

    return result_layout


def dash_app(flask_app):
    app = dash.Dash(
        server=flask_app, name='Dashboard', url_base_pathname='/visualisation/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    times = np.array([datetime(2023, 1, 1), datetime(2023, 1, 2)])
    depth = np.array([1, 2])
    temp = np.array([[1, 1], [1, 1]])

    color_scale = 'portland'
    heatmap = go.Heatmap(z=temp,
                         y=depth,
                         x=times,
                         colorscale=color_scale,
                         colorbar=dict(orientation='h', thicknessmode='pixels', thickness=20, outlinecolor='white',
                                       outlinewidth=1, lenmode='pixels', len=250, tickfont=dict(color='black'),
                                       yanchor='top', x=0.7, y=1.14)
                         )

    contour = go.Contour(z=temp,
                         y=depth,
                         x=times,
                         colorscale=color_scale,
                         colorbar=dict(orientation='h', thicknessmode='pixels', thickness=20, outlinecolor='white',
                                       outlinewidth=1, lenmode='pixels', len=250, tickfont=dict(color='black'),
                                       yanchor='top', x=0.7, y=1.14)
                         )

    plotly_layout = go.Layout(template='plotly_white', showlegend=False, coloraxis=dict(colorbar=dict(thickness=50)),
                              margin=dict(r=0, t=35, b=0, l=0))

    app.layout = create_layout(depth, times)

    @app.callback(
        Output(component_id='hidden-div', component_property='value'),
        Input(component_id='interval-data', component_property='n_intervals')
    )
    def time_update(n):
        response = requests.get('http://127.0.0.1:5000/data/current/').json()
        if response['times'] is None:
            return 'ready'
        else:
            contour.x = np.array(str_to_datetime(response['times']))
            contour.y = np.array(response['depth'])
            contour.z = np.array(response['temp'])
            heatmap.x = contour.x
            heatmap.y = contour.y
            heatmap.z = contour.z

        return 'ready'

    @app.callback(
        [Output(component_id='matrix', component_property='figure'),
         Output(component_id='time-slider', component_property='marks'),
         Output(component_id='md-slider', component_property='min'),
         Output(component_id='md-slider', component_property='max'),
         Output(component_id='time-slider', component_property='min'),
         Output(component_id='time-slider', component_property='max'),
         ],
        [Input(component_id='md-slider', component_property='value'),
         Input(component_id='time-slider', component_property='value'),
         Input(component_id='color-list-box', component_property='value'),
         Input(component_id='matrix-list-box', component_property='value'),
         Input(component_id='interval-draw', component_property='n_intervals')]
    )
    def update_matrix(md, time, color_value, matrix_type, n):
        md = md * -1
        current_times = contour.x
        current_depth = contour.y
        min_times = min(current_times)
        max_times = max(current_times)
        min_depth = min(current_depth)
        max_depth = max(current_depth)

        marks = {
            int(min_times.timestamp()): {'label': min_times.time()},
            int(max_times.timestamp()): {'label': max_times.time()},
        }

        new_depth_line = go.Scatter(x=[min_times, max_times], y=[md, md], mode='lines',
                                    line=dict(color='black', width=0.5))
        new_time_line = go.Scatter(x=[datetime.fromtimestamp(time), datetime.fromtimestamp(time)],
                                   y=[min_depth, max_depth], mode='lines',
                                   line=dict(color='black', width=0.5))

        if matrix_type == 'contour':
            current_matrix = contour
        else:
            current_matrix = heatmap

        current_matrix.colorscale = color_value
        new_fig = go.Figure(data=[current_matrix, new_depth_line, new_time_line], layout=plotly_layout)
        new_fig.update_xaxes(title_text='Date, time', range=(min_times, max_times))
        new_fig.update_yaxes(title_text='MD [m]', range=(max_depth, min_depth))
        new_fig.update_layout(title='Temperature matrix [°С]')

        return new_fig, marks, max_depth * -1, min_depth * -1, min_times.timestamp(), max_times.timestamp()

    @app.callback(
        Output(component_id='md-line', component_property='figure'),
        [Input(component_id='time-slider', component_property='value'),
         Input(component_id='interval-draw', component_property='n_intervals')]
    )
    def update_md(time, n):
        current_times = contour.x
        current_depth = contour.y
        current_temp = contour.z

        t_value = current_temp.T[get_index(current_times, datetime.fromtimestamp(time))]
        depth_fig = go.Figure(data=go.Scatter(x=t_value, y=current_depth, mode='lines', opacity=0.75,
                                              line=dict(color='red', width=0.75)), layout=plotly_layout)
        depth_fig.update_yaxes(title_text='MD [m]', range=(max(current_depth), min(current_depth)))
        depth_fig.update_xaxes(title_text='Temperature [°C]', range=get_range(t_value, 0.1))
        depth_fig.add_shape(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1.0, y1=1.0,
                            line=dict(color='black', width=0.5))
        return depth_fig

    @app.callback(
        Output(component_id='time-line', component_property='figure'),
        [Input(component_id='md-slider', component_property='value'),
         Input(component_id='interval-draw', component_property='n_intervals')]
    )
    def update_time(md, n):
        current_times = contour.x
        current_depth = contour.y
        current_temp = contour.z

        md = md * -1
        t_value = current_temp[get_index(current_depth, md)]
        time_fig = go.Figure(data=go.Scatter(x=current_times, y=t_value, mode='lines', opacity=0.75,
                                             line=dict(color='red', width=0.75)), layout=plotly_layout)
        time_fig.update_yaxes(title_text='Temperature [°C]', range=get_range(t_value, 0.1))
        time_fig.update_xaxes(title_text='Date, time', range=(min(current_times), max(current_times)))
        time_fig.add_shape(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1.0, y1=1.0,
                           line=dict(color='black', width=0.5))
        return time_fig
    return app
