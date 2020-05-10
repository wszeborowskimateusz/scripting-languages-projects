from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Article
from .forms import CreateArticle


def article_list(request):
    articles = Article.objects.all().order_by('timestamp')
    return render(request, "articles/article_list.html", {'articles': articles})

@login_required(login_url='/accounts/login/')
def article_new(request):
    if request.method == 'POST':
        form = CreateArticle(request.POST)
        if form.is_valid():
            # Save to DB
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('articles:list')
    else:
        form = CreateArticle()
    return render(request, "articles/article_new.html", {'form': form})


def article_detail(request, slug):
    article = Article.objects.get(slug=slug)
    return render(request, "articles/article_detail.html", {'article': article})
