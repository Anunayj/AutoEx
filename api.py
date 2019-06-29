from flask import Flask, request, abort, jsonify
from waitress import serve
from time import sleep, time
import threading
import main
import queue
import json
from flask_cors import CORS
import sys

app = Flask(__name__)
CORS(app)
obj={}
queue=queue.Queue(maxsize=0)

def worker():
    while True:
        try:
            uuid=queue.get()
            print(uuid)
        except:
            pass
        obj[uuid][0].start()

def janitor():
    sleep(2700)
    for elements in obj:
        if time() - elements[1] > 2700:
            del elements

class Project:
    @app.route('/')
    def index():
        return "Hello, World!"

    @app.route('/requests', methods=['POST'])
    def requests():
        #request = (request.json['maxroll'],)
        uuid = main.randomString()
        obj[uuid] = [main.resultProcessor(int(request.json['department']), int(request.json['semester']), int(request.json['maxroll']), request.json['rollPrefix']), time()]
        queue.put(uuid)
        response = app.response_class(
        response=json.dumps({'uuid':uuid}),
        status=200,
        mimetype='application/json'
        )
        #response.headers['Access-Control-Allow-Origin'] = '*'
        return(response)

    @app.route('/progress')
    def progress():
        uuid = request.args.get('uuid')
        try:
            return jsonify({"progress":obj[uuid][0].progress.progress, "max":obj[uuid][0].maxroll,"status":"200"})
        except:
            return jsonify({"progress":"0", "max":"0","status":"901"})
    @app.route('/getfile')
    def getfile():
        uuid = request.args.get('uuid')
        try:
            file = obj[uuid][0].package()
        except Exception as e:
            print(e)
            return("901 Resoruce Not Found/Deleted" + str(e)) #File Destoryed
        # if file != 601:
        #     del obj[uuid]

        if file in [500,701,601]:
            status = file
            file = ""
        else:
            status = 200
        #601: In progress
        #701: No result
        #500: Internal error

        return jsonify({"status":status,"file":str(file)})


if __name__ == '__main__':
    workerThread = threading.Thread(target=worker, name="Worker")
    janitorThread = threading.Thread(target=janitor, name="Janitor")
    workerThread.start()
    janitorThread.start()
    serve(app, port=sys.argv[1])
    #app.run(debug=True,port='8080')
