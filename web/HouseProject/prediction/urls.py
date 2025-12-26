# File: prediction/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn rỗng '' nghĩa là trang chủ
    path('', views.index, name='index'),
]