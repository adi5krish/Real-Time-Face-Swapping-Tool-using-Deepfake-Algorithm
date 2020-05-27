# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.generic import TemplateView

from facedetect.detect import get_face_detect_data


def upload_file(image):
    fs = FileSystemStorage()
    filename = fs.save(image.name, image)
    uploaded_file_url = fs.path(filename)
    return uploaded_file_url


class ImageFaceDetect(TemplateView):
    template_name = 'image.html'

    def post(self, request, *args, **kwargs):
        print("Serving Post request for image")
        data = request.POST.get('image')
        try:
            image_data = get_face_detect_data(data)
            #print("Processed the image")
            if image_data:
                #print("Attempting to send JSON response")
                #print(JsonResponse(status=200, data={'image': image_data, 'message': 'Face detected'}))
                return JsonResponse(status=200, data={'image': image_data, 'message': 'Face detected'})
        except Exception as e:
            #print("Exception in delivering response")
            pass
        return JsonResponse(status=400, data={'errors': {'error_message': 'No face detected'}})


class LiveVideoFaceDetect(TemplateView):
    template_name = 'video.html'

    def post(self, request, *args, **kwargs):
        return JsonResponse(status=200, data={'message': 'Face detected'})
