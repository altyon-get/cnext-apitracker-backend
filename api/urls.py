# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('api-list/', APIListView.as_view(), name='api-list'),
    path('api-list/<int:pk>/', APIDetailView.as_view(), name='api-detail'),
]
