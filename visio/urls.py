from django.conf.urls import url, include
from . import views


urlpatterns = [
  url ('^$', views.home, name="home"),
  url(r'^performances', views.performances, name="performances"),
  url(r'^login', views.login, name="login"),
]