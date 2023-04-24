import dash
import requests
import numpy as np
import plotly.graph_objects as go
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

from functions.back import get_all_places
from datetime import datetime, timedelta
from dash import dcc, html, ctx, Input, Output


def get_index(array, value):
    return np.argmin(np.abs(np.array(array) - value))


def get_range(array, value):
    range_values = (min(array) - max(abs(array))*value,
                    max(array) + max(abs(array))*value)
    return range_values


def str_to_datetime(array):
    new_array = []
    for i in array:
        new_array.append(datetime.strptime(i, '%d.%m.20%y %H-%M-%S'))
    return new_array


update_times = {'10 sec': 10, '30 sec': 30,
                '1.5 min': 90, '3 min': 60 * 3,
                '5 min': 60 * 5, '10 min': 60 * 10,
                '15 min': 60 * 15}

range_times = {'30 min': 30, '1 hour': 60,
               '2 hours': 120, '6 hours': 360,
               '1 day': 1440, '7 days': 1440 * 7,
               '14 days': 1440 * 14, '30 days': 1440 * 30}


def create_layout(app, depth, times, temp):
    colors = ['portland', 'jet', 'inferno', 'magenta', 'turbo']
    color_list_box = dcc.Dropdown(colors, colors[0], id='color-list-box')
    matrix_types = ['heatmap', 'contour']
    matrix_list_box = dcc.Dropdown(matrix_types, matrix_types[0], id='matrix-list-box')
    data_time_list_box = dcc.Dropdown(['10 sec', '30 sec',
                                       '1.5 min', '3 min',
                                       '5 min', '10 min', '15 min'],
                                      '1.5 min',
                                      id='data-time-list-box')
    interval_list_box = dcc.Dropdown(['30 min', '1 hour', '2 hours',
                                      '6 hours', '1 day', '7 days',
                                      '14 days', '30 days'],
                                     '1 day',
                                     id='interval-list-box')
    all_places = get_all_places()  # вот это плохо, надо как-то переделать
    places_list_box = dcc.Dropdown(all_places, all_places[0], id='places-list-box')

    """ SLIDERS """

    depth_slider = dcc.Slider(
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
            html.Div('Time update', style={'margin-top': '5px'}),
            html.Div(data_time_list_box, style={'margin-top': '5px'}),
        ]),

        dbc.Col([
            html.Div('Data interval', style={'margin-top': '5px'}),
            html.Div(interval_list_box, style={'margin-top': '5px'}),
        ]),

        dbc.Col([
            html.Div('Well name', style={'margin-top': '5px'}),
            html.Div(places_list_box, style={'margin-top': '5px'}),
        ])
    ])

    """ MAIN LAYOUT """

    result_layout = html.Div([

        # header
        html.Div([
            dbc.Row([
                html.Img(src=app.get_asset_url('icon.png'),
                         style={'width': '200px',
                                'margin-top': '5px',
                                'margin-left': '5px'}),

                dbc.Col([
                    html.H2('DTS Monitor',
                            style={'margin-bottom': '5px',
                                   'margin-top': '5px',
                                   'text-align': 'left'}),
                    html.H6('Optical fiber',
                            style={'margin-bottom': '5px',
                                   'margin-top': '5px',
                                   'text-align': 'left'}),
                ], align='start'),

                dbc.Col([
                    html.H6(id='transfer-status')
                ], style={'text-align': 'right', 'margin-right': '5px'})

            ]),
        ], className='app-header'),

        # body
        html.Div([
            dbc.Tabs([
                dbc.Tab(tab_visual_content, label='Visualisation settings'),
                dbc.Tab(tab_update_content, label='Update settings')
            ], style={'margin-bottom': '0px'}),

            dmc.Divider(variant='solid', style={'margin-top': '25px'}),

            dbc.Row([

                dbc.Col([
                    html.Div(depth_slider, style={'margin-top': '34px'})
                ], width=1),

                dbc.Col([
                    dcc.Graph(id='matrix',
                              style={'height': '638px', 'width': '100%', 'margin-left': '10px'}),  # 'width': '800px'
                    html.Div(time_slider,
                             style={'margin-left': '30px', 'width': '100%'}),  # 'width': '720px'
                    dcc.Graph(id='time-line', style={'height': '240px', 'width': '100%',
                                                     'margin-left': '15px', 'margin-bottom': '20px'})
                    # dcc.Graph(id='time-line', style={'height': '240px', 'width': '1120px',
                    #                                  'margin-left': '15px', 'margin-bottom': '20px'})
                ], width=8),

                dbc.Col([
                    dcc.Graph(id='md-line', style={'height': '622px'}),
                    dcc.Interval(id='interval', interval=10 * 1000, n_intervals=0),  # interval in ms
                    html.Div(id='hidden-div', style={'display': 'none'}),
                ], width=3)
            ], style={'margin-top': '20px'})
        ], style={'margin-left': '5%', 'margin-right': '5%'})  # 'margin-left': '100px', 'margin-right': '100px'
    ])

    return result_layout


def dash_app(flask_app):
    app = dash.Dash(
        server=flask_app, name='Dashboard', url_base_pathname='/visualisation/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        meta_tags=[{'name': 'viewport',
                    'content': 'width=device-width, initial-scale=0.5, maximum-scale=0.7, minimum-scale=0.5'}]
    )

    times = np.array([datetime.now(), datetime.now()])
    depth = np.array([1, 2])
    temp = np.array([[0, 2], [3, 25]])

    sets = {
        'time': [min(times), max(times)],
        'depth': [min(depth), max(depth)],
        'temp': [temp.min(initial=None), temp.max(initial=None)],
    }

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

    app.layout = create_layout(app, depth, times, temp)

    # Settings update
    @app.callback(
        Output(component_id='hidden-div', component_property='value'),
        [Input(component_id='interval-list-box', component_property='value'),
         Input(component_id='places-list-box', component_property='value')]
    )
    def update_settings(interval, place):
        triggered_id = ctx.triggered_id
        if triggered_id == 'interval-list-box':
            json = {'time': range_times[interval]}
            requests.post('http://127.0.0.1:5000/current/settings/time/post/', json=json)
        elif triggered_id == 'places-list-box':
            json = {'place': place}
            requests.post('http://127.0.0.1:5000/current/settings/place/post/', json=json)
        return 'ready'

    # Data update
    @app.callback(
        Output(component_id='transfer-status', component_property='children'),
        [Input(component_id='interval', component_property='n_intervals'),
         Input(component_id='hidden-div', component_property='value')]
    )
    def time_update(n, value):

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

            max_time = datetime.now()
            min_time = max_time - timedelta(minutes=response['time-interval'])

            sets['time'] = [min_time, max_time]
            sets['depth'] = [min(contour.y), max(contour.y)]
            sets['temp'] = [contour.z.min(initial=None), contour.z.max(initial=None)]

            return 'Last update: ' + str(contour.x[-1])

    # Matrix update
    @app.callback(
        [Output(component_id='matrix', component_property='figure'),
         Output(component_id='time-slider', component_property='marks'),
         Output(component_id='md-slider', component_property='marks'),
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
         Input(component_id='transfer-status', component_property='children')]
    )
    def update_matrix(md, time, color_value, matrix_type, color_bar_range, trans_const):
        md = md * -1

        min_time = sets['time'][0]
        max_time = sets['time'][1]
        min_depth = sets['depth'][0]
        max_depth = sets['depth'][1]
        min_temp = sets['temp'][0]
        max_temp = sets['temp'][1]

        marks_t = {
            int(min_time.timestamp() + 1): min_time.strftime('%H:%M:%S'),
            int(max_time.timestamp()): max_time.strftime('%H:%M:%S'),
        }

        ticks = np.linspace(min_depth, max_depth, 5)
        marks_md = {-1*int(i): int(i) for i in ticks}

        # Update time and depth profile lines on matrix
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

        # Update color bar values
        current_matrix.zauto = False
        current_matrix.zmin = color_bar_range[0]
        current_matrix.zmax = color_bar_range[1]

        # Picture creation with limits and picture frame
        new_fig = go.Figure(data=[current_matrix, new_depth_line, new_time_line], layout=plotly_layout)
        new_fig.update_xaxes(title_text='Date, time', autorange=False, range=(min_time, max_time))  # Time limit
        new_fig.update_yaxes(title_text='Cable length [m]', autorange=False, range=(max_depth, min_depth))  # Depth limit
        new_fig.update_layout(title={'text': 'Thermogram 2D [°С]', 'y': 0.989, 'font': dict(size=17)},
                              font=dict(family='Century Gothic', size=13))
        new_fig.add_shape(type='rect', xref='paper', yref='paper',  # Picture frame
                          x0=0, y0=0, x1=1.0, y1=1.0,
                          line=dict(color='black', width=0.5))

        # Zoom controller when picture update
        new_fig.layout.uirevision = True

        min_time = min_time.timestamp()
        max_time = max_time.timestamp()
        return new_fig, marks_t, marks_md, max_depth * -1, min_depth * -1, min_time, max_time, min_temp, max_temp

    # Update depth picture
    @app.callback(
        Output(component_id='md-line', component_property='figure'),
        [Input(component_id='time-slider', component_property='value'),
         Input(component_id='transfer-status', component_property='children')])
    def update_md(time, trans_const):
        current_times = contour.x
        current_depth = contour.y
        current_temp = contour.z

        t_value = current_temp.T[get_index(current_times, datetime.fromtimestamp(time))]
        depth_fig = go.Figure(data=go.Scatter(x=t_value, y=current_depth, mode='lines', opacity=0.75,
                                              line=dict(color='red', width=0.75)), layout=plotly_layout)
        depth_fig.update_yaxes(title_text='Cable length [m]', range=(max(current_depth), min(current_depth)))
        depth_fig.update_xaxes(title_text='Temperature [°C]', range=get_range(t_value, 0.1))
        depth_fig.add_shape(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1.0, y1=1.0,
                            line=dict(color='black', width=0.5))
        depth_fig.update_layout(title={'text': 'Thermogram 1D', 'y': 0.989, 'x': 0.10, 'font': dict(size=17)},
                                margin=dict(t=55),
                                font=dict(family='Century Gothic', size=13))
        depth_fig.layout.uirevision = True
        return depth_fig

    # Update time picture
    @app.callback(
        Output(component_id='time-line', component_property='figure'),
        [Input(component_id='md-slider', component_property='value'),
         Input(component_id='transfer-status', component_property='children')])
    def update_time(md, trans_const):
        current_times = contour.x
        current_depth = contour.y
        current_temp = contour.z

        min_time = sets['time'][0]
        max_time = sets['time'][1]

        md = md * -1
        t_value = current_temp[get_index(current_depth, md)]
        time_fig = go.Figure(data=go.Scatter(x=current_times, y=t_value, mode='lines', opacity=0.75,
                                             line=dict(color='red', width=0.75)), layout=plotly_layout)
        time_fig.update_yaxes(title_text='Temperature [°C]', range=get_range(t_value, 0.1))
        time_fig.update_xaxes(title_text='Date, time', range=(min_time, max_time))
        time_fig.add_shape(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1.0, y1=1.0,
                           line=dict(color='black', width=0.5))
        time_fig.update_layout(font=dict(family='Century Gothic'))
        time_fig.layout.uirevision = True
        return time_fig

    # Change timer interval
    @app.callback(
        [Output(component_id='interval', component_property='interval')],
        [Input(component_id='data-time-list-box', component_property='value')])
    def update_data_timer(new_time):
        return [update_times[new_time] * 1000]

    return app
