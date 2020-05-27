import base64
from io import BytesIO

#import cv2
#import dlib
#import imutils
import numpy as np
from PIL import Image

# FILE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SHAPE_PREDICTOR_FILE = os.path.join(FILE_DIR, 'files/shape_predictor_68_face_landmarks.dat')
# predictor = dlib.shape_predictor(SHAPE_PREDICTOR_FILE)

#detector = dlib.get_frontal_face_detector()


def base64_decode(data):
    format, imgstr = data.split(';base64,')
    return base64.b64decode(imgstr)


def base64_encode(data):
    if data:
        return 'data:image/png;base64,' + data.decode('utf-8')


def get_face_detect_data(data):
    nparr = np.fromstring(base64_decode(data), np.uint8)
    img = Image.open(BytesIO(nparr))
    image_data = detectImage(img)
    return base64_encode(image_data)


def detectImage(image):
    #image = imutils.resize(image, width=500)
    # rects = detector(image, 1)
    # for (i, rect) in enumerate(rects):
    #     (x, y, w, h) = face_utils.rect_to_bb(rect)
    #     cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    #     cv2.putText(image, "Face".format(i + 1), (x - 10, y - 10),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # if rects:
    #     output = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    #     buffer = BytesIO()
    #     img = Image.fromarray(output)
    #     img.save(buffer, format="png")
    #     encoded_string = base64.b64encode(buffer.getvalue())
    #     return encoded_string
    output = image.convert('LA')
    buffer = BytesIO()
    #img = Image.fromarray(output)
    output.save(buffer, format="png")
    encoded_string = base64.b64encode(buffer.getvalue())
    return encoded_string