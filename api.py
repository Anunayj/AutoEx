from flask import Flask, request, abort, jsonify
from time import sleep, time
import threading
import get_result_real
import queue
app = Flask(__name__)

obj=[]
queue=queue.Queue(maxsize=0)

def worker:
    while True:
        try:
            uuid=queue.get()
        except:
            pass
        obj[uuid][0].start()
def janitor:
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
        request = (request.json['maxroll'],)
        uuid = get_result_real.randomString()
        obj[uuid] = [get_result_real.resultProcessor(request.json['department'], request.json['semester'], request.json['maxroll'], request.json['rollPrefix']), time()]
        queue.put(uuid)
        return(uuid)

    @app.route('/progress')
    def progress():
        uuid = request.args.get('uuid')
        try:
            return jsonify({"progress":obj[uuid][0].progress.progress, "max":obj[uuid][0].maxroll})
        else:
            return(901)
    @app.route('/getfile')
    def getfile():
        uuid = request.args.get('uuid')
        try:
            file = obj[uuid][0].package()
        except:
            return(901) #File Destoryed
        del obj[uuid]
        if file in [500,701,601]
            return(file)
        pass


if __name__ == '__main__':
    app.run(debug=True,port='8080')
    workerThread = threading.Thread(target=worker, name="Worker")
    janitorThread = threading.Thread(target=janitor, name="Janitor")
    thread.start()
