from app import server, dash_application

from flask import redirect, url_for, jsonify, request
from functions.back import post_date


@server.route('/')
@server.route('/index')
def index():
    return redirect(url_for('dash_visual'))


""" API """


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
