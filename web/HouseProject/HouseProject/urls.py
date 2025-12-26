# File: HouseProject/urls.py
from django.contrib import admin
from django.urls import path, include  # <--- Nhớ thêm chữ 'include' ở đây

urlpatterns = [
    path('admin/', admin.site.urls),

    # Chuyển hướng mọi truy cập vào trang chủ sang file urls của app prediction
    path('', include('prediction.urls')),
]