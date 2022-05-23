from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload, name='upload'),
    path('like-post', views.like_post, name='like-post'),
    path('settings', views.settings, name='settings'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
]