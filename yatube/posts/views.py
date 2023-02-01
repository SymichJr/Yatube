from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from constants import SHOW_TEN

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def page_num(request, obj):
    paginator = Paginator(obj, SHOW_TEN)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20 * 1)
def index(request):
    posts = Post.objects.all()
    template = "posts/index.html"
    page_obj = page_num(request, posts)
    context = {"page_obj": page_obj}
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = page_num(request, posts)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    template = "posts/group_list.html"
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    all_author_posts = author.posts.all()
    posts_count = all_author_posts.count()
    page_obj = page_num(request, all_author_posts)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    context = {
        "author": author,
        "page_obj": page_obj,
        "posts_count": posts_count,
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.filter(author=post.author).all().count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        "post": post,
        "post_count": post_count,
        "form": form,
        "comments": comments,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", post.author)
        return render(request, "posts/post_create.html", {"form": form})
    form = PostForm()
    return render(request, "posts/post_create.html", {"form": form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post.id)
    post = Post.objects.get(id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if request.POST and form.is_valid():
        post = form.save()
        return redirect("posts:post_detail", post.id)
    form = PostForm(instance=post)
    return render(
        request,
        "posts/post_create.html",
        {
            "form": form,
            "group": post.group,
            "is_edit": True,
        },
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    follower = Follow.objects.filter(user=request.user).values_list(
        "author_id", flat=True
    )
    post = Post.objects.filter(author_id__in=follower)
    page_obj = page_num(request, post)
    context = {
        "post": post,
        "page_obj": page_obj,
        "title": "Избранные посты",
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author and not (
        author.following.filter(user_id=request.user.id).exists()
    ):
        Follow.objects.create(user=request.user, author=author)
    return redirect("posts:follow_index")


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:follow_index")
