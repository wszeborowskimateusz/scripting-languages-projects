from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, name='list'),
    path('new/', views.article_new, name='new'),
    url(r'^(?P<slug>[\w-]+)/$', views.article_detail, name='detail'),
]