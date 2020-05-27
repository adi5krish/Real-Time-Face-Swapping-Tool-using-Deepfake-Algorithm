from Model import Model
import os
import time
import numpy as np
import cv2
import base64
from faces_detect import DetectedFace

class ModelPrediction:

  def __init__(self, models):
    self.models = models

  def predict(self, instances, *args, **kwargs):
    print(instances)

    # load input image and grab its spatial dimensions
    string_img = base64.b64decode(instances[0])
    nparr = np.fromstring(string_img, np.uint8)
    
    # decode image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    (h, w) = image.shape[:2]

    # Run the Detection network and process results
    detections = self.facedetection(image)
    box = detections[0, 0, 0, 3:7] * np.array([w, h, w, h])
    box = box.astype("int")
    (startX, startY, endX, endY) = box
    face_width = (endX-startX)
    face_height = (endY-startY)

    # Run the Landmark Extraction network
    landmarks = self.extractLBFlandmarks(image, np.array([ [startX, startY, face_width, face_height] ]))

    # Create DetectedFace()
    detected_face = DetectedFace(image, startX, endX - startX,
                             startY, endY - startY, 
                             image.shape[:-1] , landmarks)

    #Declare some constants
    padding, face_size, size = 48, 256, 64

    # Preprocess image for autoencoder
    detected_face.load_aligned(image, face_size, padding, align_eyes=False)
    src_face = detected_face.aligned_face
    crop = slice(padding, face_size - padding)
    process_face = src_face[crop, crop]
    old_face = process_face.copy()
    process_face = cv2.resize(process_face, (size, size), interpolation=cv2.INTER_AREA)
    process_face = np.expand_dims(process_face, 0)

    # Autoencoder pass
    new_face = self.models[2](process_face/255.0)[0]
    new_face = np.clip(new_face * 255, 0, 255).astype(np.uint8)

    # Postprocessing
    new_face = cv2.resize( new_face, (face_size - padding * 2, face_size - padding * 2), interpolation=cv2.INTER_CUBIC)
    self.adjust_avg_color(old_face, new_face)
    self.smooth_mask(old_face, new_face)
    new_face = self.superpose(src_face, new_face, crop)
    new_image = image.copy()
    cv2.warpAffine(
                new_face,
                detected_face.adjusted_matrix,
                (detected_face.frame_dims[1], detected_face.frame_dims[0]),
                new_image,
                flags=cv2.WARP_INVERSE_MAP | cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_TRANSPARENT)

    retval, buffer = cv2.imencode('.png', new_image)
    encoded_string = base64.b64encode(buffer.tostring()).decode('utf-8')

    return encoded_string

  @classmethod
  def from_path(cls, model_dir):
    models = []
    proto_path = os.path.join(model_dir, 'models/deploy.prototxt.txt')
    detect_path = os.path.join(model_dir, 'models/res10_300x300_ssd_iter_140000.caffemodel')
    models.append(cv2.dnn.readNetFromCaffe(proto_path, detect_path))

    landmarks_model_path = os.path.join(model_dir, 'models/lbfmodel.yaml')
    models.append(cv2.face.createFacemarkLBF())
    models[1].loadModel(landmarks_model_path)

    autoencoder = Model(os.path.join(model_dir, 'models/'), 1)
    autoencoder.load(True)
    models.append(autoencoder.converter(False))

    return cls(models)

  def facedetection(self, image):
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    self.models[0].setInput(blob)
    detections = self.models[0].forward()

    return detections

  def extractLBFlandmarks(self, image, boxes):
    status, landmarks = self.models[1].fit(image, boxes)

    landmarks = landmarks[0][0,:,:].astype('int')
    return landmarks

  def adjust_avg_color(self, old_face, new_face):
    """ Perform average color adjustment """
    for i in range(new_face.shape[-1]):
      old_avg = old_face[:, :, i].mean()
      new_avg = new_face[:, :, i].mean()
      diff_int = (int)(old_avg - new_avg)
      for int_h in range(new_face.shape[0]):
        for int_w in range(new_face.shape[1]):
          temp = (new_face[int_h, int_w, i] + diff_int)
          if temp < 0:
              new_face[int_h, int_w, i] = 0
          elif temp > 255:
              new_face[int_h, int_w, i] = 255
          else:
              new_face[int_h, int_w, i] = temp

  def smooth_mask(self, old_face, new_face):
    """ Smooth the mask """
    width, height, _ = new_face.shape
    crop = slice(0, width)
    mask = np.zeros_like(new_face)
    mask[height // 15:-height // 15, width // 15:-width // 15, :] = 255
    mask = cv2.GaussianBlur(mask,  # pylint: disable=no-member
                            (15, 15),
                            10)
    new_face[crop, crop] = (mask / 255 * new_face +
                            (1 - mask / 255) * old_face)

  def superpose(self, src_face, new_face, crop):
    """ Crop Face """
    new_image = src_face.copy()
    new_image[crop, crop] = new_face
    return new_image