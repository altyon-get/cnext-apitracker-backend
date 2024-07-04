from django.urls import path
from .views import *

urlpatterns = [
    path('api-list/', APIListView.as_view(), name='api-list'),
    path('api-list/<str:pk>/', APIDetailView.as_view(), name='api-detail'),
    path('api-list/<str:pk>/call-logs/', APICallLogListView.as_view(), name='api-call-logs'),
    path('hit-api/<str:pk>/', hit_api_and_log, name='hit_api_and_log'),
]
