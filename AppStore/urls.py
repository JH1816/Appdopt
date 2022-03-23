"""AppStore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import app.views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', app.views.login_page, name='login'),
    path('logout/', app.views.logout_page, name = "logout"),
    path('register', app.views.register, name='register'),
    path('index', app.views.index, name = 'index'),
    path('index/add', app.views.addUser, name='add'),
    path('index/adminView/<str:username>', app.views.adminView, name = 'adminView'),
    path('<str:username>/view/<str:id>', app.views.view, name='view'),
    path('<str:username>/post', app.views.post, name='post'),
    path('<str:username>/profile', app.views.profile, name='profile'),
    path('<str:username>/mypost', app.views.mypost, name='mypost'),
    path('edit/<str:username>', app.views.edit, name='edit'),
    path('postView/<int:post_id>', app.views.postView, name = 'postView'),
    path('postEdit/<int:post_id>', app.views.postEdit, name = 'postEdit'),
    path('<str:username>/userpostEdit/<int:post_id>', app.views.userpostEdit, name = 'userpostEdit'),
    path('<str:username>', app.views.home, name='home'),
]
