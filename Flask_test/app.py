from flask import Flask, render_template, json
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config['REDIS_URL'] = "redis://:pwd@127.0.0.1:6379/0"   # pwd填 redis 密码，没有可忽略
redis_client = FlaskRedis(app)


@app.route('/proxy')
def index():
    result = redis_client.zrange(name="proxy", start=0, end=-1, withscores=True)
    handle_result = [(i[0].decode('utf-8'), i[1]) for i in result[-10:]]
    return render_template("index.html", obj=handle_result)


if __name__ == '__main__':
    app.run()
