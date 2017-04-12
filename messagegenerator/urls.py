"""labresults URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views

app_name = 'messagegenerator'
urlpatterns = [
    url(r'^ordertest', views.order_test_home, name="order_test_home"),
    url(r'^posthl7message', views.post_hl7_message, name="post_h7_message"),
    url(r'^gettests', views.get_ordered_tests, name="get_ordered_tests"),
    url(r'^gettakentests', views.get_taken_tests, name="get_taken_tests"),
    url(r'^getdoctorsoncall', views.get_doctors_on_call, name="get_doctors_on_call"),
    url(r'^login', views.login, name="login"),
    url(r'^', views.home, name="home"),
]

