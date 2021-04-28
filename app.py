from weather_chatbot import get_response
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chatbot_response():
    msg = request.form["msg"]
    response = get_response(msg)
    return response

if __name__ == '__main__':
    app.run()