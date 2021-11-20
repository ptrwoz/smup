from django.urls import path

from app.auth import authViews

urlpatterns = [
    path('', authViews.index, name='index'),
]