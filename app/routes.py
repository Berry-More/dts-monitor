from app import app
from app.forms import MessageForm, SFTPForm

from flask import render_template, redirect, url_for, jsonify
from functions import load_las, get_data


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = SFTPForm()
    if form.validate_on_submit():
        hostname = form.hostname.data
        port = form.port.data
        username = form.username.data
        password = form.password.data
        print('\n' + hostname, port)
        print(username, password)
        print('Data received!\n')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/get_data/', methods=['GET'])
def get_data_for_dash():
    las_files = load_las(r'D:\Temp\Work\НОЦ ГПН\Optical fiber\New_program\getting_data')
    if len(las_files) > 15:
        las_files = las_files[-15::]
    times, depth, temp = get_data(las_files)
    return jsonify({'times': times, 'depth': depth, 'temp': temp.tolist()})


@app.route('/message/', methods=['GET', 'POST'])
def message():
    form = MessageForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        print('\n'+name)
        print(email)
        print(message)
        print('Data received!\n')
        return redirect(url_for('message'))
    return render_template('message.html', form=form)
