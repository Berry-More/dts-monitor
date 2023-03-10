from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, IPAddress


class SFTPForm(FlaskForm):
    hostname = StringField('Имя хоста:', validators=[IPAddress(), InputRequired()])
    port = StringField('Порт:', validators=[InputRequired()])
    username = StringField('Имя пользователя:', validators=[InputRequired()])
    password = PasswordField('Пароль:', validators=[InputRequired()])
    submit = SubmitField('Подключиться')
