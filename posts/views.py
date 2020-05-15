from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from users.forms import User


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"page": page, 'paginator': paginator, "group": group})


@login_required
def new_post(request):
    words = ["Создание", "Новая"]
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            Post.objects.create(
                author=request.user, 
                text=form.cleaned_data["text"],
                group=form.cleaned_data["group"],
                image=form.cleaned_data["image"]
            )
            return redirect("index")
        return render(request, "new_post.html", {"form":form, "words": words})
    form = PostForm()
    return render(request, "new_post.html", {"form":form, "words": words})


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    post = Post.objects.filter(author=user_profile)

    post_list = Post.objects.filter(author=user_profile).order_by("-pub_date").all()
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=user_profile).exists()
    else:
        following = False

    return render(request, "profile.html", {
        "user_profile": user_profile,
        "page": page,
        "paginator": paginator,
        "post": post,
        "following": following
    })


def post_view(request, username, post_id):
    user_profile = get_object_or_404(User, username=username)
    post = Post.objects.get(id=post_id)
    count_post = Post.objects.filter(author=user_profile).count()
    
    form = CommentForm()
    comments = Comment.objects.filter(post=post_id).order_by("created")
    return render(request, "post.html", {
        "user_profile": user_profile,
        "post": post,
        "count_post": count_post,
        "form": form,
        "comments": comments
    })


@login_required
def post_edit(request, username, post_id):
    cur_user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=cur_user)
    words = ["Редактирование", "Редактировать"]
    if request.user != cur_user:
        return redirect("post", username=username, post_id=post_id)

    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect ("post", username=request.user.username, post_id=post_id) 
    form = PostForm(instance=post)
    return render(request, "new_post.html", {"form": form, "post": post, "words": words})
    

def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=user)
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                post=Post.objects.get(id=post_id),
                author=request.user,
                text=form.cleaned_data["text"]                
            )
            return redirect("post", username=username, post_id=post_id)
    form = CommentForm()
    return redirect("post", username=username, post_id=post_id)


@login_required
def follow_index(request):
    follow_set = Follow.objects.filter(user=request.user)
    post_list = Post.objects.filter(author__in=[follow.author_id for follow in follow_set]).order_by("-pub_date")

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {
        "page": page,
        'paginator': paginator,
        "post_list": post_list
    })


@login_required
def profile_follow(request, username):
    profile = request.user
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=profile, author=author).exists()

    if following == True:
        return redirect("profile", username=username)
    elif profile != author:
        Follow.objects.create(user=profile, author=author)
        return redirect("profile", username=username)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    profile = request.user
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=profile, author=author).exists()

    if following == True:
        Follow.objects.filter(user=profile, author=author).delete()
        return redirect("profile", username=username)
    return redirect("profile", username=username)
    