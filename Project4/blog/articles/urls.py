from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, name='list'),
    path('new/', views.article_new, name='new'),
    url(r'^delete-comment/(?P<comment_id>\d+)/$', views.delete_comment, name='delete_comment'),
    url(r'^add-reaction/(?P<reaction_type>[\w-]+)/(?P<slug>[\w-]+)/$', views.add_reaction, name='add_reaction'),
    url(r'^(?P<slug>[\w-]+)/$', views.article_detail, name='detail'),
]