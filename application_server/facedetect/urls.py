from django.conf.urls import url
from django.urls import path

from facedetect.views import ImageFaceDetect, LiveVideoFaceDetect

app_name="facedetect"

urlpatterns = [
	url(r'^face-detect/video/$', LiveVideoFaceDetect.as_view(), name='live_video'),
    url(r'^face-detect/image/$', ImageFaceDetect.as_view(), name='image'),
    url(r'^$', LiveVideoFaceDetect.as_view(), name='live_video'),
]

# urlpatterns = [
#     path(r'^face-detect/image/$', ImageFaceDetect.as_view(), name='image'),
#     path(r'^face-detect/video/$', LiveVideoFaceDetect.as_view(), name='live_video'),
# ]
