from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, InputRequired, IPAddress


class MessageForm(FlaskForm):
    name = StringField('Имя:', validators=[DataRequired()])
    email = StringField('Email:', validators=[Email()])
    message = TextAreaField('Сообщение:', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class SFTPForm(FlaskForm):
    hostname = StringField('Имя хоста:', validators=[IPAddress(), InputRequired()])
    port = StringField('Порт:', validators=[InputRequired()])
    username = StringField('Имя пользователя:', validators=[InputRequired()])
    password = PasswordField('Пароль:', validators=[InputRequired()])
    submit = SubmitField('Подключиться')
