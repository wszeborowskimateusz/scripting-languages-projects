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
    comments = Comment.objects.all().filter(article=article).order_by('-timestamp')
    reactions = Reaction.objects.all().filter(article=article)
    positiveReactions = reactions.filter(reaction_type=Reaction.ReactionType.HAPPY)
    neutralReactions = reactions.filter(reaction_type=Reaction.ReactionType.NEUTRAL)
    negativeReactions = reactions.filter(reaction_type=Reaction.ReactionType.SAD)

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
        slug = comment.article.slug 
        comment.delete()
        return redirect('articles:detail', slug=slug)
