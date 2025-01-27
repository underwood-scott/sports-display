from flask import Flask, jsonify, request, current_app
from run_display import run_display

app = Flask(__name__)

@app.route('/')
def start_display():
    run_display('/home/scott.underwood/Documents/sports-sign/sports-display/6x10.bdf')

def serve():
    app.run(host="0.0.0.0")

if __name__ == "__main__":
    serve()
