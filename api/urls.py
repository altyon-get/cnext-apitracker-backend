from django.urls import path
from .views import *

urlpatterns = [
    path('api-list/', APIListView.as_view(), name='api-list'),
    path('api-list/<str:api_id>/', APIDetailView.as_view(), name='api-detail'),
    path('api-list/<str:api_id>/call-logs/', APICallLogListView.as_view(), name='api-call-logs'),
    path('hit-api/<str:api_id>/', HitApiAndLogView.as_view(), name='hit_api_and_log'),
    path('upload-json/', UploadJSONView.as_view(), name='upload-json'),
]