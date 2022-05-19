from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post
from .view_utils import throwError, checkImageFile, checkVideoFile, splitFeed, parseVideoId

@login_required(login_url='login')
def index(request):
    user_profile = Profile.objects.get(user=request.user)
    feed = splitFeed(Post.objects.all(), 3)

    return render(request, 'index.html', {'user_profile': user_profile, 'feed': feed})

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