from app import server, dash_application

from flask import redirect, url_for, jsonify, request
from back import post_data, get_data, get_all_places, get_full_depth, get_last_time


@server.route('/')
@server.route('/index')
def index():
    return redirect(url_for('dash_visual'))


""" API """


# Get data
@server.route('/current/data/<interval>/<place>/<depth_min>/<depth_max>/', methods=['GET'])
def data_sending(interval, place, depth_min, depth_max):
    try:
        full_depth_interval = get_full_depth(int(interval), place)
    except ValueError:
        full_depth_interval = None
    try:
        times, depth, temp = get_data(int(interval) + 20, place, float(depth_min), float(depth_max))
        return jsonify({'times': times, 'depth': depth, 'temp': temp.tolist(), 'depth-interval': full_depth_interval})
    except ValueError as error:
        return jsonify({'times': None, 'depth': None, 'temp': str(error), 'depth-interval': full_depth_interval})


# Get last time in DB
@server.route('/current/data/times/last/<place>')
def last_time_sending(place):
    return jsonify({'last_time': get_last_time(place)})


# Get places
@server.route('/current/data/places/', methods=['GET'])
def places_sending():
    try:
        places = get_all_places()
        return jsonify({'places': list(places)})
    except ValueError('Нет доступных скважин'):
        return jsonify({'places': None})


# Post data
@server.route('/current/data/post/', methods=['POST'])
def data_posting():
    if request.json:
        new_file = {
            'time': request.json['time'],
            'depth': request.json['depth'],
            'temp': request.json['temp'],
            'place': request.json['place']
        }
        post_data(new_file)
        return jsonify({'new_file': new_file}), 201


""" VISUALISATION """


@server.route('/visualisation/')
def dash_visual():
    return dash_application.index()
