import json
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.forms import ModelForm, Textarea
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Post, Profile, User

class NewPostForm(ModelForm):
    post_text = forms.CharField(label='', widget=Textarea(attrs={'class': 'box'}))

def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "posts": page_obj
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=user)
                profile.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            profile = Profile.objects.create(user=user)
            profile.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
@login_required
def newpost(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    post_text = data.get("post", "")
    profile = Profile.objects.get(user=request.user)

    post = Post(post_by=profile, message=post_text)
    post.save()

    posts = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "posts": page_obj
    })

@csrf_exempt
def like_unlikeposts(request, post_id):

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    if request.method == "PUT":
        data = json.loads(request.body)
        profile = Profile.objects.get(user=request.user)
        if data.get("like_unlike") == "like":
            post.likes.add(profile)
        elif data.get("like_unlike") == "unlike": 
            post.likes.remove(profile)
        post.save()
        return JsonResponse({"like_count": post.likes.count(), "id": post_id})

    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)

@csrf_exempt
def follow(request, username): 

    try: 
        view_user = User.objects.get(username=username)
        profile_of_view_user = Profile.objects.get(user=view_user)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if request.method == "PUT":
        data = json.loads(request.body)
        profile_of_current_user = Profile.objects.get(user=request.user)

        if data.get("follow_unfollow") == "follow":
            profile_of_view_user.followers.add(request.user)
            profile_of_current_user.following.add(view_user)

        elif data.get("follow_unfollow") == "unfollow": 
            profile_of_view_user.followers.remove(request.user)
            profile_of_current_user.following.remove(view_user)

        profile_of_view_user.save()
        profile_of_current_user.save()
        return JsonResponse({"followers_count": profile_of_view_user.followers.count(), "id": profile_of_view_user.id})

    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)

def profile(request, username):
    user = User.objects.get(username=username)
    view_profile = Profile.objects.get(user=user)
    posts = Post.objects.filter(post_by=view_profile).all().order_by("-timestamp")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile.html", {
        "view_profile": view_profile, "posts": page_obj
    })

@login_required
def following(request):
    posts = Post.objects.filter(post_by__followers=request.user).all().order_by("-timestamp")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        "posts": page_obj
    })

@csrf_exempt
@login_required
def edit(request, post_id):

    try:
        post = Post.objects.get(pk=post_id)
        poster = post.poster()
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    
    if request.user.username != poster:
        return JsonResponse({"error": "Not authorized to edit this post"}, status=404)

    if request.method != 'PUT':
        return JsonResponse({"error": "PUT request required."}, status=404)

    data = json.loads(request.body)
    print(data.get("message"))
    post_text = data.get("message")
    post.message = post_text
    post.save()

    return JsonResponse(post.message, safe=False)
