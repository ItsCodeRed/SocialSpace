from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowerCount
from .view_utils import throwError, checkImageFile, checkVideoFile, splitFeed, parseVideoId
from itertools import chain
import random

@login_required(login_url='login')
def index(request):
    user_profile = Profile.objects.get(user=request.user)

    followed_users = []
    post_ids = set()

    following_relations = FollowerCount.objects.filter(follower=request.user.username)
    for following_relation in following_relations:
        user = User.objects.get(username=following_relation.user)
        profile = Profile.objects.get(user=user)
        followed_users.append(profile)
        posts = Post.objects.filter(profile=profile).all()
        for post in posts:
            post_ids.add(post.id)

    posts = Post.objects.filter(id__in = post_ids).all().order_by('date').reverse()
    feed = splitFeed(posts, 3)

    all_users = Profile.objects.all()
    suggestions = [x for x in list(all_users) if (x not in followed_users and x != user_profile)]
    random.shuffle(suggestions)
    suggestions = list(chain(suggestions))

    return render(request, 'index.html', {'user_profile': user_profile, 'feed': feed, 'suggestions': suggestions[:4]})

@login_required(login_url='login')
def upload(request):
    if request.method == 'POST':
        file = request.FILES.get('file_upload')            
        video = file if checkVideoFile(file) else None
        image = file if checkImageFile(file) else None

        youtube_id = ''
        if 'video_link' in request.POST:
            youtube_id = parseVideoId(request.POST['video_link'])
        caption = request.POST['caption']
        user_profile = Profile.objects.get(user=request.user)

        new_post = Post.objects.create(profile=user_profile, image=image, video=video, yt_id=youtube_id, caption=caption)
        new_post.save()

    return redirect('/')

@login_required(login_url='login')
def search(request):
    user_profile = Profile.objects.get(user=request.user)

    search_term = ''
    if request.GET.get('username'):
        search_term = request.GET['username']

    found_users = User.objects.filter(username__icontains=search_term)
    search_result = Profile.objects.filter(user__in=found_users)

    return render(request, 'search.html', {'user_profile': user_profile, 'search_term': search_term, 'search_results': search_result})

@login_required(login_url='login')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)
    my_like = LikePost.objects.filter(post_id=post_id, username=username).first()

    if my_like == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.likes += 1
        post.save()
    else:
        my_like.delete()
        post.likes -= 1
        post.save()

    return redirect('/')

@login_required(login_url='login')
def profile(request, user):
    user_object = User.objects.get(username=user)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(profile=user_profile)
    num_posts = len(user_posts)
    follower_count = len(FollowerCount.objects.filter(user=user))
    following_count = len(FollowerCount.objects.filter(follower=user))

    if FollowerCount.objects.filter(follower=request.user.username,user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    context = {
        'user_object': user_object,
        'profile': user_profile,
        'posts': user_posts,
        'num_posts': num_posts,
        'button_text': button_text,
        'follower_count': follower_count,
        'following_count': following_count
    }

    return render(request, 'profile.html', context)

@login_required(login_url='login')
def follow(request):
    if request.method == 'POST':
        follower = request.user.username
        user = request.POST['user']

        if FollowerCount.objects.filter(follower=follower,user=user).first():
            delete_follower = FollowerCount.objects.get(follower=follower,user=user)
            delete_follower.delete()
            profile = Profile.objects.get(user=User.objects.get(username=user))
            profile.follower_count -= 1
            profile.save()
            return redirect('/profile/' + user)
        else:
            new_follower = FollowerCount.objects.create(follower=follower,user=user)
            new_follower.save()
            profile = Profile.objects.get(user=User.objects.get(username=user))
            profile.follower_count += 1
            profile.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')

@login_required(login_url='login')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        image = request.FILES.get('image')

        if checkImageFile(image) != None:
            user_profile.profileimg = image

        user_profile.user.first_name = request.POST['first_name']
        user_profile.user.last_name = request.POST['last_name']
        user_profile.user.save()
        user_profile.bio = request.POST['bio']
        user_profile.location = request.POST['location']
        user_profile.save()

    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):
    if request.method != 'POST':
        return render(request, 'signup.html')

    errors_thrown = 0

    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    confirm_password = request.POST['confirm_password']

    if username == '':
        errors_thrown = throwError(request, 'Username required', errors_thrown)

    if email == '':
        errors_thrown = throwError(request, 'Email required', errors_thrown)

    if password == '':
        errors_thrown = throwError(request, 'Password required', errors_thrown)

    if confirm_password == '':
        errors_thrown = throwError(request, 'Must confirm password', errors_thrown)

    if password != confirm_password and password != '' and confirm_password != '':
        errors_thrown = throwError(request, 'Failed to confirm password', errors_thrown)

    if User.objects.filter(email=email).exists():
        errors_thrown = throwError(request, 'Email is taken', errors_thrown)

    if User.objects.filter(username=username).exists():
        errors_thrown = throwError(request, 'Username is taken', errors_thrown)

    if errors_thrown > 0:
        return redirect('signup')

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    # Log user in and redirect to settings page
    user_login = auth.authenticate(username=username, password=password)
    auth.login(request, user_login)

    # Create a profile object for the new user
    user_model = User.objects.get(username=username)
    new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
    new_profile.save()

    return redirect('settings')

def login(request):
    if request.method != 'POST':
        return render(request, 'login.html')

    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username, password=password)

    if not User.objects.filter(username=username).exists():
        throwError(request, 'No user exists with that username')
        return render(request, 'login.html')

    if user is None:
        throwError(request, 'Incorrect password')
        return render(request, 'login.html')

    auth.login(request, user)
    return redirect('/')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')