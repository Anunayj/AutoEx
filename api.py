from flask import Flask, request, abort, jsonify
from time import sleep, time
import threading
import main
import queue
app = Flask(__name__)

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
<<<<<<< HEAD
    sleep(2700)
=======
    sleep(270000)
>>>>>>> a1fe83f8847a0bdf1fa299a0d2c3206fd49f88cd
    for elements in obj:
        if time() - elements[1] > 270000:
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
        return(uuid)

    @app.route('/progress')
    def progress():
        uuid = request.args.get('uuid')
        try:
            return jsonify({"progress":obj[uuid][0].progress.progress, "max":obj[uuid][0].maxroll})
        except:
            return("901")
    @app.route('/getfile')
    def getfile():
        uuid = request.args.get('uuid')
        try:
            file = obj[uuid][0].package()
        except:
<<<<<<< HEAD
            return("901 Resoruce Not Found/Deleted") #File Destoryed
=======
            return("901") #File Destoryed
>>>>>>> a1fe83f8847a0bdf1fa299a0d2c3206fd49f88cd
        if file != 601:
            del obj[uuid]

        # if file in [500,701,601]:
        #601: In progress
        #701: No result
        #500: Internal error
        return(str(file))
<<<<<<< HEAD
=======
        # else:

        pass
>>>>>>> a1fe83f8847a0bdf1fa299a0d2c3206fd49f88cd


if __name__ == '__main__':
    workerThread = threading.Thread(target=worker, name="Worker")
    janitorThread = threading.Thread(target=janitor, name="Janitor")
    workerThread.start()
    janitorThread.start()
<<<<<<< HEAD
    app.run(debug=False,port='8080')
=======
    app.run(debug=True,port='8080')
>>>>>>> a1fe83f8847a0bdf1fa299a0d2c3206fd49f88cd
