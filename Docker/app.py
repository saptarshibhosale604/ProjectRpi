from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hi there"

@app.route('/other')
def other():
    return "Hey there, This is me"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
