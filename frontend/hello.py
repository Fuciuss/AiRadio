from flask import Flask, request
app = Flask(__name__)

CURRENT_TRACK = "smooth jazz"


@app.route('/currenttrack', methods=['POST'])
def current_track():
    global CURRENT_TRACK
    CURRENT_TRACK = request.json['track_name']
    print(f"Current track: {CURRENT_TRACK}")
    return request.json



@app.route('/')
def hello_world():
    return f"""<div style="color: white; background-color: black; text">
    
    <h1>Hello, World!</h1>
    <h2>Now playing: {CURRENT_TRACK}</h2>
    
    
    </div>"""

if __name__ == '__main__':
    app.run(debug=True, port=8080)
