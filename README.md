# Real-Time-Face-Swapping-Tool-using-Deepfake-Algorithm
Implemented a cloud-based real-time face-swapping tool to swap faces in a video. Developed a 3-tier architecture to enable efficient deployment of deepfake based face swapping. The proposed 3-tier architecture could potentially be used for deploying many other
real time applications which rely on complex machine learning models. The Application server serves as an entry point for the user. This provides the user an interface to the underlying cloud infrastructure. The user is then connected to the WebSocket server for real-time duplex communication. Finally, an autoscaling ML inferencing server does the heavy-lifting.

Installation -

The installation of Client Application Server and Websocket is similar as both are hosted on the App Engine. The Deepfake model is pre-trained and loaded and used in order to get the merged image. The steps included in installing each component is given below, these instructions are given for Ubuntu 18.04:

1) Client Application Server

a) Install all the required python library using ‘pip install -r requirements’

b) To test the client application locally, we used the command ‘python manage.py runserver’

c) To run the client on the cloud we need to collect the static files in STATIC_ROOT

folder using ‘python manage.py collectstatic’ and run ‘gcloud app deploy’ to start deployment.

2) Websocket Server

a) Install all the required python library using ‘pip install -r requirements’

b) To test the websocket locally, we used the command, ‘gunicorn -b 127.0.0.1:8001 -k flask_sockets.worker main:app’.

c) To run the websocket on the cloud we used ‘gcloud app deploy’.

3) Deepfake Prediction model

a) The deepfake prediction model has to be deployed as a custom routine on the AI Platform as a prediction routine.

b) Run setup.py to package the custom routine and the additional dependencies.

c) Create a Model on AI Platform and deploy the created package as a version. It is important to specify Pediction. ModelPrediction as the main class which instructs the routine about loading and inferencing from the model.

Functionalities of the Program

Client Application Server - 

The client contains 3 important files i.e. app.yaml, static files and facedetect files. The functionalities of each file is given below:

- App.yaml contains the configuration of the app’s setting. It tells the URL how to respond to handlers and static files. In this case we load the static html files from the static folder using app.yaml.

- Static files contain the HTML and CSS code for our web application which enables the users to access the face swapping video stream.

- The facedetect folder contains the Django default files generated while initializing the Django framework. The views.py is responsible for the request handling of the image. Urls.py redirects the application according to the path provided. Settings.py holds the
configuration values required for the web application to run.

Websocket Server

The Websocket server similar to client server has app.yaml, and also as it is a background task we have no static files and the functions to be executed in main.py which is deployed via Flask application.

- App.yaml contains the entrypoint for the application which is given as a gunicorn command which redirects it to main.py.

- Main.py receives the client frames, makes an api call to the deepfake model and returns the results to the client.

Deepfake Prediction Model

The Deepfake Prediction model is deployed on the AI Platform which provides a PaaS infrastructure to provide machine learning inferencing as a service. The websocket server sends API requests and based on the volume of these requests and current resources, the AI Platform provides automatic scaling.  Following is a description of the files it contains:

- Prediction.py contains the ModelPrediction class which is defined based on the custom routine format. It defines the routines for loading the deepfake model and for performing inferencing.
