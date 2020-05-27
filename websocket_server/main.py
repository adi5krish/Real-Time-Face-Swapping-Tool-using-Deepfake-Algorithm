from flask import Flask
from flask_sockets import Sockets
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjjvtlhfl1232#'
sockets = Sockets(app)

credentials = ServiceAccountCredentials.from_json_keyfile_name('cse546-276423-33d9698813ad.json')
api = discovery.build('ml', 'v1', credentials=credentials, discoveryServiceUrl='https://storage.googleapis.com/cloud-ml/discovery/ml_v1_discovery.json')
detector_name = 'projects/{}/models/{}/'.format('cse546-276423', 'face_extraction')
deepfake_name = 'projects/{}/models/{}/'.format('cse546-276423', 'deepfake')

@sockets.route('/websocket')
def handle_frame(ws):
    global client
    while not ws.closed:
        message = ws.receive()
        if message is None:  # message is "None" if the client has closed.
            continue
        print("Received a message")
        _, imgstr = message.split(';base64,')
        extraction_response = api.projects().predict(body={'instances':[imgstr]}, name=detector_name).execute()
        
        request = {}
        data = {}
        data['image'] = imgstr
        data['startX'] = extraction_response['predictions']['startX']
        data['startY'] = extraction_response['predictions']['startY']
        data['width'] = extraction_response['predictions']['width']
        data['height'] = extraction_response['predictions']['height']
        data['landmarks'] = extraction_response['predictions']['landmarks']
        request['instances'] = [data]

        response = api.projects().predict(body=request, name=deepfake_name).execute()

        output = 'data:image/png;base64,'+response['predictions']
        ws.send(output)
        # Send the message to all clients connected to this webserver
        # process. (To support multiple processes or instances, an
        # extra-instance storage or messaging system would be required.)
        # clients = ws.handler.server.clients.values()
        # for client in clients:
        #     #print(client.address, client.ws)
        #     client.ws.send(output)

if __name__ == '__main__':
    print("""
This can not be run directly because the Flask development server does not
support web sockets. Instead, use gunicorn:
gunicorn -b 127.0.0.1:8080 -k flask_sockets.worker main:app
""")