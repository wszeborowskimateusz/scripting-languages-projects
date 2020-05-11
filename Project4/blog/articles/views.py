from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from .models import Article, Comment, Reaction
from .forms import CreateArticle, CreateComment


def article_list(request):
    articles = Article.objects.all().order_by('-timestamp')
    return render(request, "articles/article_list.html", {'articles': articles})

@login_required(login_url='/accounts/login/')
def article_edit(request, id=None):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    if id:
        is_edit = True
        article = get_object_or_404(Article, id=id)
    else:
        is_edit = False
        article = Article(author=request.user)
    form = CreateArticle(request.POST or None, instance=article)
    if request.method == 'POST' and form.is_valid():
        # Save to DB
        new_article = form.save(article)
        return redirect('articles:list')

    return render(request, "articles/article_new.html", {'form': form, 'is_edit': is_edit, 'article': article})


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    comments = Comment.objects.all().filter(article=article).order_by('-timestamp')
    reactions = Reaction.objects.all().filter(article=article)
    positiveReactions = reactions.filter(reaction_type=Reaction.ReactionType.HAPPY)
    neutralReactions = reactions.filter(reaction_type=Reaction.ReactionType.NEUTRAL)
    negativeReactions = reactions.filter(reaction_type=Reaction.ReactionType.SAD)

    if request.method == 'POST':
        commentForm = CreateComment(request.POST)
        if commentForm.is_valid():
            if not request.user.is_authenticated:
                return HttpResponseForbidden()
            comment = commentForm.save(commit=False)
            comment.author = request.user
            comment.article = article
            comment.save()
            return redirect('articles:detail', slug=slug)
    else:
        commentForm = CreateComment()
    return render(request, "articles/article_detail.html", 
        {'article': article, 'comments': comments, 'commentForm': commentForm, 
        'happyReactions': positiveReactions, 'neutralReactions': neutralReactions, 'sadReactions': negativeReactions})

@login_required(login_url='/accounts/login/')
def add_reaction(request, reaction_type, slug):
    if request.method == 'POST':
        article = get_object_or_404(Article, slug=slug)
        try:
            # If user already gave a reaction to this post this will not throw exception
            reaction = Reaction.objects.all().filter(article=article, author=request.user)
            reaction.delete()
        except Reaction.DoesNotExist:
            pass
        
        if reaction_type == 'positive':
            r_type = Reaction.ReactionType.HAPPY
        elif reaction_type == 'neutral': 
            r_type = Reaction.ReactionType.NEUTRAL
        elif reaction_type == 'negative':
            r_type = Reaction.ReactionType.SAD
        new_reaction = Reaction(article=article, author=request.user, reaction_type=r_type)
        new_reaction.save()

        print(f"Got reaction: {reaction_type} to article with slug {slug} from user {request.user}")
        return redirect('articles:detail', slug=slug)

@login_required(login_url='/accounts/login/')
def delete_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        if (not request.user.is_superuser) and (comment.author != request.user):
            return HttpResponseForbidden()
        slug = comment.article.slug 
        comment.delete()
        return redirect('articles:detail', slug=slug)

@login_required(login_url='/accounts/login/')
def delete_article(request, article_id):
    if request.method == 'POST':
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        article = get_object_or_404(Article, id=article_id)
        article.delete()
        return redirect('articles:list')