"""public_voices URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from django.contrib import admin
import public_voices.views as views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('login/', views.login),
    path('signup/', views.signup),
    # path('set_password/<str:user_id>/', views.set_password),
    path('logout/', views.logout),
    path('hot_topics/', views.hot_topics),
    path('create_topic/', views.create_topic),
    path('topic/<str:topic_id>/', views.topic),
    path('create_comment/<str:topic_id>/', views.create_comment),
    path('analyze/<str:topic_id>/', views.analyze)
]
