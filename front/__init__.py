import dash
import requests
import numpy as np
import plotly.graph_objects as go
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

from datetime import datetime, timedelta
from dash import dcc, ctx, html, Input, Output, State


def get_index(array, value):
    return np.argmin(np.abs(np.array(array) - value))


def get_range(min_v, max_v,  value):
    add_v = max(abs(np.array([min_v, max_v])))
    range_values = (min_v - add_v*value,
                    max_v + add_v*value)
    return range_values


def str_to_datetime(array):
    new_array = []
    for i in array:
        new_array.append(datetime.strptime(i, '%d.%m.20%y %H-%M-%S'))
    return new_array


update_times = {'10 сек': 10, '30 сек': 30,
                '1.5 мин': 90, '3 мин': 60 * 3,
                '5 мин': 60 * 5, '10 мин': 60 * 10,
                '15 мин': 60 * 15}

range_times = {'30 мин': 30, '1 час': 60,
               '2 часа': 120, '6 часов': 360,
               '1 день': 1440, '7 дней': 1440 * 7,
               '14 дней': 1440 * 14, '30 дней': 1440 * 30}


def create_layout(app, depth, times, temp):
    colors = ['portland', 'jet', 'inferno', 'magenta', 'turbo']
    color_list_box = dcc.Dropdown(colors, colors[0], id='color-list-box')
    matrix_types = ['heatmap', 'contour']
    matrix_list_box = dcc.Dropdown(matrix_types, matrix_types[0], id='matrix-list-box')
    data_time_list_box = dcc.Dropdown(['10 сек', '30 сек',
                                       '1.5 мин', '3 мин',
                                       '5 мин', '10 мин', '15 мин'],
                                      '1.5 мин',
                                      id='data-time-list-box')
    interval_list_box = dcc.Dropdown(['30 мин', '1 час', '2 часа',
                                      '6 часов', '1 день', '7 дней',
                                      '14 дней', '30 дней'],
                                     '7 дней',
                                     id='interval-list-box')
    all_places = ['Kluchi']
    places_list_box = dcc.Dropdown(all_places, all_places[0], id='places-list-box')

    """ SLIDERS """

    depth_profile_slider = dcc.Slider(
        id='md-slider',
        max=min(depth) * -1,
        min=max(depth) * -1,
        step=2,
        value=min(depth) * -1,
        marks={
            int(min(depth)) * -1: int(min(depth)),
            int(max(depth)) * -1: int(max(depth)),
        },
        vertical=True,
        verticalHeight=570,
        included=False,
        tooltip={'placement': 'left', 'always_visible': True}
    )

    time_profile_slider = dcc.Slider(
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
        min=-20,
        max=50,
        value=[temp.min(), temp.max()],
        tooltip={'placement': 'bottom', 'always_visible': True}
    )

    depth_slider = dcc.RangeSlider(
        id='depth-slider',
        min=min(depth),
        max=max(depth),
        step=2,
        tooltip={'placement': 'bottom', 'always_visible': True}
    )

    """ TABS CONTENT """

    tab_visual_content = dbc.Row([

        dbc.Col([
            html.Div('Текущий колорбар', style={'margin-top': '5px'}),  # Current colorscale
            html.Div(color_list_box, style={'margin-top': '10px'}),
        ]),

        dbc.Col([
            html.Div('Текущий тип изображения', style={'margin-top': '5px'}),  # Current matrix type
            html.Div(matrix_list_box, style={'margin-top': '10px'}),
        ]),

        dbc.Col([
            html.Div('Интервал колорбара', style={'margin-top': '5px', 'margin-left': '15px'}),  # Color bar interval
            html.Div(color_bar_slider, style={'margin-top': '15px'}),
        ])

    ])

    tab_update_content = dbc.Row([

        dbc.Col([
            html.Div('Время обновления', style={'margin-top': '5px'}),  # Time update
            html.Div(data_time_list_box, style={'margin-top': '5px'}),
        ]),

        dbc.Col([
            html.Div('Интервал по времени', style={'margin-top': '5px'}),  # Data interval
            html.Div(interval_list_box, style={'margin-top': '5px'}),
        ]),

        dbc.Col([
            html.Div('Название скважины', style={'margin-top': '5px'}),  # Well name
            html.Div(places_list_box, style={'margin-top': '5px'}),
        ]),

        dbc.Col([
            html.Div('Интервал по глубине',  # Cable length interval
                     style={'margin-top': '5px', 'margin-left': '15px'}),
            html.Div(depth_slider, style={'margin-top': '15px'}),
        ], width=4)
    ])

    """ MAIN LAYOUT """

    result_layout = html.Div([

        # header
        html.Div([
            dbc.Row([

                html.Img(src=app.get_asset_url('icon.png'), style={'width': '85px', 'height': '70px',
                                                                   'margin-top': '5px', 'margin-left': '20px'}),

                dbc.Col([
                    html.H3('DTS Мониторинг', style={'margin-top': '7px', 'text-align': 'left'}),
                    html.P('Разработано s.ponasenko@g.nsu.ru'),  # Developed by
                ], align='start'),

                dbc.Col([
                    html.H6(id='transfer-status'),
                ], style={'text-align': 'right', 'margin-right': '10px'})
            ]),
        ], className='app-header', style={'margin-bottom': '0px'}),

        # body
        html.Div([
            dbc.Tabs([
                dbc.Tab(tab_visual_content, label='Параметры визуализации'),  # Visualisation settings
                dbc.Tab(tab_update_content, label='Параметры обновления')  # Update settings
            ], style={'margin-bottom': '0px'}),

            dmc.Divider(variant='solid', style={'margin-top': '25px'}),

            dbc.Row([

                dbc.Col([
                    html.Div(depth_profile_slider, style={'margin-top': '34px'})
                ], width=1),

                dbc.Col([
                    dcc.Graph(id='matrix', style={'height': '638px', 'width': '100%', 'margin-left': '10px'}),
                    html.Div(time_profile_slider, style={'margin-left': '30px', 'width': '100%'}),
                    dcc.Graph(id='time-line', style={'height': '240px', 'width': '100%',
                                                     'margin-left': '15px', 'margin-bottom': '20px'})
                ], width=8),

                dbc.Col([
                    dcc.Graph(id='md-line', style={'height': '622px'}),
                    # Add vertical line
                    dbc.Button('Добавить вертикальный профиль', id='add-md-graph', n_clicks=0, className='me-1',
                               color='info', style={'margin-left': '40px', 'margin-top': '10px', 'width': '90%'}),
                    # Add horizontal line
                    dbc.Button('Добавить горизонтальный профиль', id='add-time-graph', n_clicks=0, className='me-1',
                               color='info', style={'margin-left': '40px', 'margin-top': '10px', 'width': '90%'}),
                    # Clear
                    dbc.Button('Удалить профили', id='clear-graphs', n_clicks=0, className='me-1', color='info',
                               style={'margin-left': '40px', 'margin-top': '10px', 'width': '90%'}),
                    dcc.Interval(id='interval', interval=10 * 1000, n_intervals=0),  # interval in ms
                    dcc.Store(data=[1, 2], id='current-memory', storage_type='memory', clear_data=False),
                ], width=3)
            ], style={'margin-top': '20px'})
        ], style={'margin-left': '5%', 'margin-right': '5%'}),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Img(src=app.get_asset_url('pish.png'),
                             style={'width': '203px', 'height': '58px',
                                    'margin-top': '25px'})
                ]),
                dbc.Col([
                    html.Img(src=app.get_asset_url('nsu.png'), style={'width': '154px', 'height': '58px',
                                                                      'margin-top': '25px'})
                ])
            ]),
        ], className='app-ender', style={'margin-top': '20px', 'text-align': 'center'}),
    ])

    return result_layout


def dash_app(flask_app):
    app = dash.Dash(
        server=flask_app, title='DTS Мониторинг', name='Dashboard', url_base_pathname='/visualisation/',  # DTS Monitor
        external_stylesheets=[dbc.themes.MINTY],
        meta_tags=[{'name': 'viewport',
                    'content': 'width=device-width, initial-scale=0.5, maximum-scale=0.7, minimum-scale=0.5'}]
    )

    times = np.array([datetime.now(), datetime.now()])
    depth = np.array([1, 2])
    temp = np.array([[0, 2], [3, 25]])

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
        template='plotly_white', coloraxis=dict(colorbar=dict(thickness=50)), showlegend=True,
        legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01, bgcolor='rgba(0,0,0,0)'),
        margin=dict(r=0, t=35, b=0, l=0)
    )

    app.layout = create_layout(app, depth, times, temp)

    # Data update
    @app.callback(
        Output(component_id='transfer-status', component_property='children'),
        Output(component_id='places-list-box', component_property='options'),
        Output(component_id='depth-slider', component_property='min'),
        Output(component_id='depth-slider', component_property='max'),
        Output(component_id='depth-slider', component_property='marks'),
        Input(component_id='interval', component_property='n_intervals'),
        Input(component_id='interval-list-box', component_property='value'),
        Input(component_id='places-list-box', component_property='value'),
        Input(component_id='depth-slider', component_property='value'),
    )
    def time_update(n, time_interval, place, depth_interval):
        if depth_interval is None:
            depth_interval = [0.0, 0.0]
        url = 'http://127.0.0.1:5000/current/data/' + str(range_times[time_interval]) + '/' + place + '/'
        url = url + str(depth_interval[0]) + '/' + str(depth_interval[1]) + '/'
        response = requests.get(url).json()
        resp_places = requests.get('http://127.0.0.1:5000/current/data/places').json()

        if not response['depth-interval'] is None:
            full_depth_interval = response['depth-interval']
        else:
            full_depth_interval = [0, 1]

        if resp_places['places'] is None:
            places = ['bad request']
        else:
            places = resp_places['places']

        if response['times'] is None:
            status = 'bad request'
            if not response['temp'] is None:
                status = response['temp']
            marks = None
        else:
            contour.x = np.array(str_to_datetime(response['times']))
            contour.y = np.array(response['depth'])
            contour.z = np.array(response['temp'])
            heatmap.x = contour.x
            heatmap.y = contour.y
            heatmap.z = contour.z
            status = 'Последнее обновление данных:  ' + str(contour.x[-1])  # Last update

            ticks = np.linspace(full_depth_interval[0], full_depth_interval[1], 5, dtype=int)
            ticks[ticks % 2 != 0] += 1
            marks = {int(i): int(i) for i in ticks}

        return status, places, full_depth_interval[0], full_depth_interval[1], marks

    # Matrix update
    @app.callback(
        Output(component_id='matrix', component_property='figure'),
        Output(component_id='time-slider', component_property='marks'),
        Output(component_id='md-slider', component_property='marks'),
        Output(component_id='md-slider', component_property='min'),
        Output(component_id='md-slider', component_property='max'),
        Output(component_id='time-slider', component_property='min'),
        Output(component_id='time-slider', component_property='max'),
        Input(component_id='md-slider', component_property='value'),
        Input(component_id='time-slider', component_property='value'),
        Input(component_id='color-list-box', component_property='value'),
        Input(component_id='matrix-list-box', component_property='value'),
        Input(component_id='color-bar-slider', component_property='value'),
        Input(component_id='transfer-status', component_property='children'),
        Input(component_id='current-memory', component_property='data'),
        State(component_id='interval-list-box', component_property='value')
    )
    def update_matrix(md, time, color_value, matrix_type, cb_range, t_const, memory_data, time_interval):
        md = md * -1
        max_time = datetime.now()
        min_time = max_time - timedelta(minutes=range_times[time_interval])

        min_depth = min(contour.y)
        max_depth = max(contour.y)

        marks_t = {
            int(min_time.timestamp() + 1): min_time.strftime('%H:%M:%S'),
            int(max_time.timestamp()): max_time.strftime('%H:%M:%S'),
        }

        ticks = np.linspace(min_depth, max_depth, 5, dtype=int)
        ticks[ticks % 2 != 0] += 1
        marks_md = {-1*int(i): int(i) for i in ticks}

        # Update time and depth profile lines on matrix
        if memory_data is None:
            memory_data = {'time': [], 'depth': []}

        if matrix_type == 'contour':
            current_matrix = contour
        else:
            current_matrix = heatmap
        current_matrix.colorscale = color_value

        lines = [current_matrix]
        for i in memory_data['depth']:
            lines.append(go.Scatter(x=[min_time, max_time], y=[i, i], mode='lines',
                                    line=dict(color='black', width=0.5, dash='dash')))
        lines.append(go.Scatter(x=[min_time, max_time], y=[md, md], mode='lines', line=dict(color='black', width=0.5)))
        for i in memory_data['time']:
            lines.append(go.Scatter(x=[datetime.fromtimestamp(i), datetime.fromtimestamp(i)], y=[min_depth, max_depth],
                                    mode='lines', line=dict(color='black', width=0.5, dash='dash')))
        lines.append(go.Scatter(x=[datetime.fromtimestamp(time), datetime.fromtimestamp(time)],
                                y=[min_depth, max_depth], mode='lines', line=dict(color='black', width=0.5)))

        # Update color bar values
        current_matrix.zauto = False
        current_matrix.zmin = cb_range[0]
        current_matrix.zmax = cb_range[1]

        # Picture creation with limits and picture frame
        new_fig = go.Figure(data=lines, layout=plotly_layout)
        # Date, time
        new_fig.update_xaxes(title_text='Дата, время', autorange=False, range=(min_time, max_time))  # Time limit
        # Cable length
        new_fig.update_yaxes(title_text='Длина кабеля [м]', autorange=False, range=(max_depth, min_depth))  # Depth
        # Thermogram 2D
        new_fig.update_layout(title={'text': 'Термограмма 2D [°С]', 'y': 0.989, 'font': dict(size=17)},
                              showlegend=False, font=dict(family='Century Gothic', size=13))
        new_fig.add_shape(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1.0, y1=1.0,
                          line=dict(color='black', width=0.5))

        # Zoom controller when picture update
        new_fig.layout.uirevision = True

        min_time = min_time.timestamp()
        max_time = max_time.timestamp()
        return new_fig, marks_t, marks_md, max_depth * -1, min_depth * -1, min_time, max_time

    # Update depth picture
    @app.callback(
        Output(component_id='md-line', component_property='figure'),
        Input(component_id='time-slider', component_property='value'),
        Input(component_id='current-memory', component_property='data'),
        Input(component_id='transfer-status', component_property='children')
    )
    def update_md(time, memory_data, t_const):
        graphs = []
        if memory_data is None:
            memory_data = {'time': [], 'depth': []}
        for i in memory_data['time']:
            t_value = contour.z.T[get_index(contour.x, datetime.fromtimestamp(i))]
            graphs.append(go.Scatter(x=t_value, y=contour.y, mode='lines', opacity=0.75,
                                     name=datetime.fromtimestamp(i).strftime('%H:%M %d-%m-%y'), line=dict(width=0.75)))
        t_value = contour.z.T[get_index(contour.x, datetime.fromtimestamp(time))]
        graphs.append(go.Scatter(x=t_value, y=contour.y, mode='lines', opacity=0.75, name='текущий профиль',
                                 line=dict(color='red', width=1)))

        temp_max = -1000
        temp_min = 1000
        for i in range(len(graphs)):
            if max(graphs[i].x) > temp_max:
                temp_max = max(graphs[i].x)
            if min(graphs[i].x) < temp_min:
                temp_min = min(graphs[i].x)

        depth_fig = go.Figure(data=graphs, layout=plotly_layout)
        # Cable length
        depth_fig.update_yaxes(title_text='Длина кабеля [м]', range=(max(contour.y), min(contour.y)))
        # depth_fig.update_yaxes(title_text='Cable length [m]', range=(depth_range[1], depth_range[0]))
        # Temperature
        depth_fig.update_xaxes(title_text='Температура [°C]', range=get_range(temp_min, temp_max, 0.1))

        depth_fig.add_shape(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1.0, y1=1.0,
                            line=dict(color='black', width=0.5))
        # Thermogram 1D
        depth_fig.update_layout(title={'text': 'Термограмма 1D', 'y': 0.989, 'x': 0.10, 'font': dict(size=17)},
                                margin=dict(t=55), font=dict(family='Century Gothic', size=13))
        depth_fig.layout.uirevision = True
        return depth_fig

    # Update time picture
    @app.callback(
        Output(component_id='time-line', component_property='figure'),
        Input(component_id='md-slider', component_property='value'),
        Input(component_id='current-memory', component_property='data'),
        Input(component_id='transfer-status', component_property='children'),
        State(component_id='interval-list-box', component_property='value')
    )
    def update_time(md, memory_data, t_const, time_interval):
        max_time = datetime.now()
        min_time = max_time - timedelta(minutes=range_times[time_interval])

        md = md * -1
        graphs = []
        if memory_data is None:
            memory_data = {'time': [], 'depth': []}
        for i in memory_data['depth']:
            t_value = contour.z[get_index(contour.y, i)]
            graphs.append(go.Scatter(x=contour.x, y=t_value, mode='lines', name=str(i), opacity=0.75,
                                     line=dict(width=0.75)))
        t_value = contour.z[get_index(contour.y, md)]
        graphs.append(go.Scatter(x=contour.x, y=t_value, mode='lines', name='текущий профиль', opacity=0.75,
                                 line=dict(color='red', width=1)))

        temp_max = -1000
        temp_min = 1000
        for i in range(len(graphs)):
            if max(graphs[i].y) > temp_max:
                temp_max = max(graphs[i].y)
            if min(graphs[i].y) < temp_min:
                temp_min = min(graphs[i].y)

        time_fig = go.Figure(data=graphs, layout=plotly_layout)
        # Temperature
        time_fig.update_yaxes(title_text='Температура [°C]', range=get_range(temp_min, temp_max, 0.1))
        # Date, time
        time_fig.update_xaxes(title_text='Дата, время', range=(min_time, max_time))
        time_fig.add_shape(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1.0, y1=1.0,
                           line=dict(color='black', width=0.5))
        time_fig.update_layout(font=dict(family='Century Gothic'))
        time_fig.layout.uirevision = True
        return time_fig

    # Change timer interval
    @app.callback(
        Output(component_id='interval', component_property='interval'),
        Input(component_id='data-time-list-box', component_property='value')
    )
    def update_data_timer(new_time):
        return [update_times[new_time] * 1000]

    @app.callback(
        Output(component_id='current-memory', component_property='data'),
        Input(component_id='clear-graphs', component_property='n_clicks'),
        Input(component_id='add-md-graph', component_property='n_clicks'),
        Input(component_id='add-time-graph', component_property='n_clicks'),
        State(component_id='current-memory', component_property='data'),
        State(component_id='md-slider', component_property='value'),
        State(component_id='time-slider', component_property='value')
    )
    def add_graph(n_depth, n_time, n_clear, memory_data, md, time):
        if memory_data is None:
            memory_data = {'time': [], 'depth': []}
        triggered_id = ctx.triggered_id
        if triggered_id == 'clear-graphs':
            memory_data['depth'] = []
            memory_data['time'] = []
            return memory_data
        elif triggered_id == 'add-time-graph':
            memory_data['depth'].append(md * -1)
            return memory_data
        elif triggered_id == 'add-md-graph':
            memory_data['time'].append(time)
            return memory_data

    return app
