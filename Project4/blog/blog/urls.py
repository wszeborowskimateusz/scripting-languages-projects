from django.contrib import admin
from django.urls import path, include

from . import views
from articles import views as article_views

handler404 = 'blog.views.handler404'
#handler500 = 'my_app.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls')),
    path('accounts/', include('accounts.urls')),
    path('', article_views.article_list, name='home'),
]
