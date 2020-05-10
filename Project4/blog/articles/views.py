from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Article, Comment, Reaction
from .forms import CreateArticle, CreateComment


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
    article = get_object_or_404(Article, slug=slug)
    comments = Comment.objects.all().filter(article=article)
    reactions = Reaction.objects.all().filter(article=article)


    if request.method == 'POST':
        commentForm = CreateComment(request.POST)
        if commentForm.is_valid():
            comment = commentForm.save(commit=False)
            comment.author = request.user
            comment.article = article
            comment.save()
            return redirect('articles:detail', slug=slug)
    else:
        commentForm = CreateComment()
    return render(request, "articles/article_detail.html", 
        {'article': article, 'comments': comments, 'commentForm': commentForm, 'reactions': reactions})

def add_reaction(request, slug):
    article = get_object_or_404(Article, slug=slug)
    print("Adding this reaction")
    return redirect('articles:detail', slug=slug)
