import webbrowser

from app import app


if __name__ == '__main__':
    # # открываю браузер и запускаю приложение
    # webbrowser.open('http://127.0.0.1:5000/login/', new=0)
    app.run(debug=True)  # arg: debug=True
