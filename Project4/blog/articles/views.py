from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Article


def article_list(request):
    articles = Article.objects.all().order_by('timestamp')
    return render(request, "articles/article_list.html", {'articles': articles})

@login_required(login_url='/accounts/login/')
def article_new(request):
    return render(request, "articles/article_new.html")


def article_detail(request, slug):
    article = Article.objects.get(slug=slug)
    return render(request, "articles/article_detail.html", {'article': article})
