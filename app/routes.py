from app import server, dash_application

from flask import redirect, url_for, jsonify, request
from functions.back import get_data, post_date


settings = {
    'time-interval': 60,  # minutes
}


@server.route('/')
@server.route('/index')
def index():
    return redirect(url_for('dash_visual'))


""" API """


# Get settings
@server.route('/current/settings/', methods=['GET'])
def settings_sending():
    return jsonify(settings)


# Get data
@server.route('/current/data/', methods=['GET'])
def data_sending():
    try:
        times, depth, temp = get_data(settings['time-interval'])
        return jsonify({'times': times, 'depth': depth, 'temp': temp.tolist()})

    except ValueError:
        return jsonify({'times': None, 'depth': None, 'temp': None})


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


# Post interval set
@server.route('/current/data/interval/', methods=['POST'])
def interval_posting():
    if request.json:
        settings['time-interval'] = request.json['interval']
        return jsonify({'sets': settings}), 201


""" VISUALISATION """


@server.route('/visualisation/')
def dash_visual():
    return dash_application.index()
