from app import app
from app.forms import SFTPForm

from flask import render_template, redirect, url_for, jsonify
from functions import load_las, get_data


settings = {
    'time-interval': 15  # file numbers
}


@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('login'))


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


@app.route('/data/current/', methods=['GET'])
def data_sending():
    try:
        las_files = load_las(r'D:\Temp\Work\НОЦ ГПН\Optical fiber\New_program\getting_data')
        if len(las_files) > settings['time-interval']:
            las_files = las_files[-1*settings['time-interval']::]
        times, depth, temp = get_data(las_files)
        return jsonify({'times': times, 'depth': depth, 'temp': temp.tolist()})

    except OSError:
        return jsonify({'times': None, 'depth': None, 'temp': None})

