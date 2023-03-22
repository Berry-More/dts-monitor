import dash
import requests
import numpy as np
import plotly.graph_objects as go
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

from datetime import datetime, timedelta
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
fig_time_list_box = dcc.Dropdown(['1', '2', '5', '10', '30', '60'], '5', id='fig-time-list-box')
data_time_list_box = dcc.Dropdown(['10', '30', '60', '120', '180', '300', '600'], '10', id='data-time-list-box')
interval_list_box = dcc.Dropdown(['30', '60', '120', '360', '1440', '10080'], '360', id='interval-list-box')


def create_layout(depth, times, temp):

    """ SLIDERS """

    depth_slider = dcc.Slider(
        id='md-slider',
        max=min(depth) * -1,
        min=max(depth) * -1,
        value=min(depth) * -1,
        vertical=True,
        verticalHeight=570,
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

    color_bar_slider = dcc.RangeSlider(
        id='color-bar-slider',
        min=temp.min(),
        max=temp.max(),
        value=[temp.min(), temp.max()]
    )

    """ TABS CONTENT """

    tab_visual_content = dbc.Row([

        dbc.Col([
            html.Div('Current colorscale', style={'margin-top': '5px'}),
            html.Div(color_list_box, style={'margin-top': '5px'}),
        ]),

        dbc.Col([
            html.Div('Current matrix type', style={'margin-top': '5px'}),
            html.Div(matrix_list_box, style={'margin-top': '5px'}),
        ]),

        dbc.Col([
            html.Div('Color bar interval', style={'margin-top': '5px', 'margin-left': '15px'}),
            html.Div(color_bar_slider, style={'margin-top': '15px'}),
        ])

    ])

    tab_update_content = dbc.Row([

        dbc.Col([
            html.Div('Figure update time [s]', style={'margin-top': '5px'}),
            html.Div(fig_time_list_box, style={'margin-top': '5px'}),
        ]),

        dbc.Col([
            html.Div('Data update time [s]', style={'margin-top': '5px'}),
            html.Div(data_time_list_box, style={'margin-top': '5px'}),
        ]),

        dbc.Col([
            html.Div('Data interval [m]', style={'margin-top': '5px'}),
            html.Div(interval_list_box, style={'margin-top': '5px'}),
        ])

    ])

    """ MAIN LAYOUT """

    result_layout = html.Div([

        dbc.Row([

            dbc.Col([
                html.H2('DTS Monitor'),
            ], style={'margin-bottom': '5px', 'margin-top': '5px'}),

            dbc.Col([
                html.H6(id='transfer-status')
            ], style={'text-align': 'right'})

        ]),

        dbc.Tabs([
            dbc.Tab(tab_visual_content, label='Visualisation settings'),
            dbc.Tab(tab_update_content, label='Update settings')
        ], style={'margin-bottom': '0px'}),

        dmc.Divider(variant='solid', style={'margin-top': '25px'}),

        dbc.Row([

            dbc.Col([
                html.Div('MD slider',
                         style={'text-align': 'left', 'margin-left': '5px', 'width': '100px'}),
                html.Div(depth_slider, style={'margin-top': '12px'})
            ], width=1),

            dbc.Col([
                dcc.Graph(id='matrix',
                          style={'height': '638px', 'width': '100%', 'margin-left': '10px'}),  # 'width': '800px'
                html.Div('Time slider',
                         style={'text-align': 'left', 'margin-left': '5px'}),
                html.Div(time_slider,
                         style={'margin-left': '30px', 'width': '100%'}),  # 'width': '720px'
                dcc.Graph(id='time-line', style={'height': '240px', 'width': '1120px',
                                                 'margin-left': '15px', 'margin-bottom': '20px'})
            ], width=8),

            dbc.Col([
                html.Div('MD graph', style={'margin-left': '40px'}),
                dcc.Graph(id='md-line', style={'height': '600px'}),
                dcc.Interval(id='interval-data', interval=10*1000, n_intervals=0),  # interval in ms
                dcc.Interval(id='interval-draw', interval=1*1000, n_intervals=0),
                html.Div(id='hidden-div', style={'display': 'none'}),
            ], width=3)
        ], style={'margin-top': '20px'})
    ], style={'margin-left': '100px', 'margin-right': '100px'})

    return result_layout


def dash_app(flask_app):
    app = dash.Dash(
        server=flask_app, name='Dashboard', url_base_pathname='/visualisation/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    times = np.array([datetime(2023, 1, 1), datetime(2023, 1, 2)])
    depth = np.array([1, 2])
    temp = np.array([[0, 20], [20, 0]])

    color_scale = 'portland'
    heatmap = go.Heatmap(
        z=temp,
        y=depth,
        x=times,
        colorscale=color_scale,
        colorbar=dict(orientation='h', thicknessmode='pixels', thickness=20, outlinecolor='white',
                      outlinewidth=1, lenmode='pixels', len=250, tickfont=dict(color='black'),
                      yanchor='top', x=0.7, y=1.11)
                         )

    contour = go.Contour(
        z=temp,
        y=depth,
        x=times,
        colorscale=color_scale,
        colorbar=dict(orientation='h', thicknessmode='pixels', thickness=20, outlinecolor='white',
                      outlinewidth=1, lenmode='pixels', len=250, tickfont=dict(color='black'),
                      yanchor='top', x=0.7, y=1.11)
                         )

    plotly_layout = go.Layout(
        template='plotly_white', showlegend=False, coloraxis=dict(colorbar=dict(thickness=50)),
        margin=dict(r=0, t=35, b=0, l=0)
    )

    app.layout = create_layout(depth, times, temp)

    @app.callback(
        Output(component_id='hidden-div', component_property='value'),
        Input(component_id='interval-list-box', component_property='value')
    )
    def update_interval(interval):
        json = {'interval': int(interval)}
        requests.post('http://127.0.0.1:5000//current/data/interval/', json=json)
        return 'ready'

    @app.callback(
        Output(component_id='transfer-status', component_property='children'),
        [Input(component_id='interval-data', component_property='n_intervals'),
         Input(component_id='interval-list-box', component_property='value')]
    )
    def time_update(n, interval):
        response = requests.get('http://127.0.0.1:5000/current/data/').json()
        if response['times'] is None:
            return 'bad request'
        else:
            contour.x = np.array(str_to_datetime(response['times']))
            contour.y = np.array(response['depth'])
            contour.z = np.array(response['temp'])
            heatmap.x = contour.x
            heatmap.y = contour.y
            heatmap.z = contour.z
        return 'Last update: ' + str(contour.x[-1])

    @app.callback(
        [Output(component_id='matrix', component_property='figure'),
         Output(component_id='time-slider', component_property='marks'),
         Output(component_id='md-slider', component_property='min'),
         Output(component_id='md-slider', component_property='max'),
         Output(component_id='time-slider', component_property='min'),
         Output(component_id='time-slider', component_property='max'),
         Output(component_id='color-bar-slider', component_property='min'),
         Output(component_id='color-bar-slider', component_property='max')
         ],
        [Input(component_id='md-slider', component_property='value'),
         Input(component_id='time-slider', component_property='value'),
         Input(component_id='color-list-box', component_property='value'),
         Input(component_id='matrix-list-box', component_property='value'),
         Input(component_id='color-bar-slider', component_property='value'),
         Input(component_id='interval-draw', component_property='n_intervals'),
         Input(component_id='interval-list-box', component_property='value')]
    )
    def update_matrix(md, time, color_value, matrix_type, color_bar_range, n, interval):
        md = md * -1
        # current_times = contour.x
        current_depth = contour.y
        # min_time = min(current_times)
        # max_time = max(current_times)
        max_time = datetime.now()
        min_time = max_time - timedelta(minutes=int(interval))
        min_depth = min(current_depth)
        max_depth = max(current_depth)
        min_temp = contour.z.min(initial=None)
        max_temp = contour.z.max(initial=None)

        marks = {
            int(min_time.timestamp()): {'label': min_time.time()},
            int(max_time.timestamp()): {'label': max_time.time()},
        }

        new_depth_line = go.Scatter(x=[min_time, max_time], y=[md, md], mode='lines',
                                    line=dict(color='black', width=0.5))
        new_time_line = go.Scatter(x=[datetime.fromtimestamp(time), datetime.fromtimestamp(time)],
                                   y=[min_depth, max_depth], mode='lines',
                                   line=dict(color='black', width=0.5))

        if matrix_type == 'contour':
            current_matrix = contour
        else:
            current_matrix = heatmap

        current_matrix.colorscale = color_value
        current_matrix.zauto = False
        current_matrix.zmin = color_bar_range[0]
        current_matrix.zmax = color_bar_range[1]
        new_fig = go.Figure(data=[current_matrix, new_depth_line, new_time_line], layout=plotly_layout)
        new_fig.update_xaxes(title_text='Date, time', range=(min_time, max_time))
        new_fig.update_yaxes(title_text='MD [m]', range=(max_depth, min_depth))
        new_fig.update_layout(title='Thermogram 2D [°С]')
        new_fig.add_shape(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1.0, y1=1.0,
                          line=dict(color='black', width=0.5))
        new_fig.layout.uirevision = True

        min_time = min_time.timestamp()
        max_time = max_time.timestamp()

        return new_fig, marks, max_depth * -1, min_depth * -1, min_time, max_time, min_temp, max_temp

    @app.callback(
        Output(component_id='md-line', component_property='figure'),
        [Input(component_id='time-slider', component_property='value'),
         Input(component_id='interval-draw', component_property='n_intervals')])
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
        depth_fig.layout.uirevision = True
        return depth_fig

    @app.callback(
        Output(component_id='time-line', component_property='figure'),
        [Input(component_id='md-slider', component_property='value'),
         Input(component_id='interval-draw', component_property='n_intervals'),
         Input(component_id='interval-list-box', component_property='value')])
    def update_time(md, n, interval):
        current_times = contour.x
        current_depth = contour.y
        current_temp = contour.z

        max_time = datetime.now()
        min_time = max_time - timedelta(minutes=int(interval))

        md = md * -1
        t_value = current_temp[get_index(current_depth, md)]
        time_fig = go.Figure(data=go.Scatter(x=current_times, y=t_value, mode='lines', opacity=0.75,
                                             line=dict(color='red', width=0.75)), layout=plotly_layout)
        time_fig.update_yaxes(title_text='Temperature [°C]', range=get_range(t_value, 0.1))
        time_fig.update_xaxes(title_text='Date, time', range=(min_time, max_time))
        time_fig.add_shape(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1.0, y1=1.0,
                           line=dict(color='black', width=0.5))
        time_fig.layout.uirevision = True
        return time_fig

    @app.callback(
        [Output(component_id='interval-data', component_property='interval')],
        [Input(component_id='data-time-list-box', component_property='value')])
    def update_data_timer(new_time):
        return [int(new_time) * 1000]

    @app.callback(
        [Output(component_id='interval-draw', component_property='interval')],
        [Input(component_id='fig-time-list-box', component_property='value')])
    def update_draw_timer(new_time):
        return [int(new_time) * 1000]

    return app
