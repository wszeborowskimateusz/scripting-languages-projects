from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, name='list'),
    path('new/', views.article_edit, name='new'),
    url(r'^edit/(?P<id>\d+)/$', views.article_edit, name='edit'),
    url(r'^delete-article/(?P<article_id>\d+)/$', views.delete_article, name='delete_article'),
    url(r'^delete-comment/(?P<comment_id>\d+)/$', views.delete_comment, name='delete_comment'),
    url(r'^add-reaction/(?P<reaction_type>[\w-]+)/(?P<slug>[\w-]+)/$', views.add_reaction, name='add_reaction'),
    url(r'^(?P<slug>[\w-]+)/$', views.article_detail, name='detail'),
]