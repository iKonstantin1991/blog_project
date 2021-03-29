from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import PER_PAGE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    latest = Post.objects.select_related('group').all()
    paginator = Paginator(latest, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'page': page,
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'new_post.html', {'form': form})

    form = PostForm(request.POST, files=request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:index')

    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following_number = author.follower.all().count()
    follower_number = author.following.all().count()
    author_posts = author.posts.all()

    user_post_quantity = author.posts.all().count()

    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    else:
        following = False

    paginator = Paginator(author_posts, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'author': author,
        'quantity': user_post_quantity,
        'following_number': following_number,
        'follower_number': follower_number,
        'following': following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    user_post_quantity = Post.objects.filter(author__username=username).count()
    author = post.author
    following_number = author.follower.all().count()
    follower_number = author.following.all().count()

    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    else:
        following = False

    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'author': author,
        'quantity': user_post_quantity,
        'form': form,
        'comments': comments,
        'following_number': following_number,
        'follower_number': follower_number,
        'following': following,
    }
    return render(request, 'post.html', context)


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)

    if not request.user == post.author:
        return redirect(
            'posts:post',
            username=username,
            post_id=post_id
        )

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post.save()
        return redirect(
            'posts:post',
            username=username,
            post_id=post_id
        )
    return render(request, 'new_post.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    redirect_to_post_page = redirect(
        'posts:post',
        username=username,
        post_id=post_id
    )
    if request.method == 'GET':
        return redirect_to_post_page

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = Post.objects.get(id=post_id)
        comment.save()
        return redirect_to_post_page

    return redirect_to_post_page


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    redirect_to_profile = redirect(
        'posts:profile',
        username=username,
    )
    if request.user == author:
        return redirect_to_profile

    Follow.objects.get_or_create(
        user=request.user,
        author=author
    )
    return redirect_to_profile


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    get_object_or_404(Follow, user=request.user, author=author).delete()
    #  Follow.objects.get(user=request.user, author=author).delete()
    return redirect(
        'posts:profile',
        username=username,
    )


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
