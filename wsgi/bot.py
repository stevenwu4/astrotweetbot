from flask import Flask, jsonify, request, render_template
from api.request import RequestWeb as rw

app = Flask(__name__)
   
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/<path:call>', methods=['GET'])
def get_data(call):
    error_msg = {'success':1, 'error':'no'}
    if request.method == 'GET':
        return jsonify(rw().determine_response(call, request.args))
    else:
        return jsonify(error_msg)
    
if __name__ == "__main__":
    app.debug = True
    app.run()
