from flask import Flask, render_template
from config import config
app = Flask(__name__)


@app.route('/')
def hello_world():
    # return 'Hello World!'
    return render_template('page.html')

if __name__ == '__main__':
    app.config.from_object(config)
    app.run(host='127.0.0.1', port=80)
