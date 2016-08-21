from flask import Flask, render_template, jsonify
from config import config, handle_config
from mongo import analyst, lagou
from data import all_job_analyst
import pymongo

app = Flask(__name__)


@app.route('/')
def index():
    table = lagou('history')
    data = []
    for job in handle_config.moniter:
        result = table.find({'name': job}).sort('timestamp', pymongo.DESCENDING)
        data.append({'text': result[0]['name'], 'count': result[0]['count']})
    return render_template('index.html', data=data)


@app.route('/json/<job>/<item>')
def json(job, item):
    table = analyst(job)
    data = table.find({'name': item}).sort('time', pymongo.DESCENDING)
    return jsonify(data[0]['data'])


@app.route('/p/<job>')
def page(job):
    return render_template('page.html', job=job)


if __name__ == '__main__':
    # app.config.from_object(config)
    app.run(host='127.0.0.1', port=4500)
