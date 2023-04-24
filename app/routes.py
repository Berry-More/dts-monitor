from app import server, dash_application

from flask import redirect, url_for, jsonify, request
from functions.back import post_date, new_get_data, get_all_places


settings = {'time': 1440, 'place': 'Kluchi'}


@server.route('/')
@server.route('/index')
def index():
    return redirect(url_for('dash_visual'))


""" API """


# Get data
@server.route('/current/data/', methods=['GET'])
def data_sending():
    try:
        times, depth, temp = new_get_data(settings['time'], settings['place'])
        return jsonify({'times': times, 'depth': depth, 'temp': temp.tolist(),
                        'time-interval': settings['time']})
    except ValueError:
        return jsonify({'times': None, 'depth': None, 'temp': None})


@server.route('/current/places/', methods=['GET'])
def get_places():
    try:
        places = get_all_places()
        return jsonify({'places': places})
    except ValueError:
        return jsonify({'places': None})


# Post new monitoring time
@server.route('/current/settings/time/post/', methods=['POST'])
def time_posting():
    if request.json:
        settings['time'] = request.json['time']
        return jsonify({'new_time': settings['time']}), 201


# Post new monitoring place
@server.route('/current/settings/place/post/', methods=['POST'])
def place_posting():
    if request.json:
        settings['place'] = request.json['place']
        return jsonify({'new_place': settings['place']}), 201


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
        post_date(new_file)
        return jsonify({'new_file': new_file}), 201


""" VISUALISATION """


@server.route('/visualisation/')
def dash_visual():
    return dash_application.index()
