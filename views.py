from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Post, Following, Likes
from .forms import postForm

import json
import datetime


def index(request):
    allposts = Post.objects.all().order_by('-created_at')
    # Pagination
    paginator = Paginator(allposts, 10) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        'page_obj': page_obj,
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
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def post(request):

    # Work the sent form
    if request.method == "POST":
        form = postForm(request.POST)
        if form.is_valid():
            # Register this post to the db
            obj = Post.objects.create(
                creator = User.objects.get(pk=request.user.id),
                content = form.cleaned_data['textarea'],
                created_at = datetime.datetime.now()
            )
            
            obj.save()

            return redirect('index')

    return render(request, "network/post.html", {
        'postForm': postForm(),
    })


@login_required
def profile(request, profile_id):

    # Is the user seeing tehir own profile or is it someone else? 
    profile_user_id = request.user.id if request.user.id == profile_id else profile_id

    followers = Following.objects.filter(following=profile_user_id).count()
    following = Following.objects.filter(follower=profile_user_id).count()
    all_user_posts = Post.objects.filter(creator=profile_user_id).order_by('-created_at')
    paginator = Paginator(all_user_posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    follow_or_unfollow = 'Unfollow' if Following.objects.filter(follower=User.objects.get(pk=request.user.id), following=profile_user_id) else 'Follow'

    return render(request, "network/profile.html", {
        'creator': User.objects.get(id=profile_user_id).username,
        'page_obj': page_obj,
        'followers': followers,
        'following': following,
        'follow_or_unfollow': follow_or_unfollow,
        'user_is_the_profile_owner': request.user.id == profile_id
    })


@login_required
def content_following(request):

    # All users that the current user follow
    all_users_beeing_followed_by_current_user = Following.objects.filter(follower=request.user.id).values()
    posts = []
    for followed_user in all_users_beeing_followed_by_current_user:
        bunch_of_posts = Post.objects.filter(creator=followed_user['following_id']).order_by('-created_at')[:10]
        for post in bunch_of_posts:
            posts.append(post)

    paginator = Paginator(posts, 10) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        'page_obj': page_obj,
    })


@csrf_exempt
@login_required
def likes(request, post_id):
    
    # Dinamiclly, like or unlike a post
    if request.method != 'POST':
        return JsonResponse({"error": "Wrong method used in this route."})

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Take a reference and all data from the found post
    post = Post.objects.get(id=post_id)

    # This variable will be changed by the try-except block
    action = ''

    # Check if the user has already liked this post
    try:
        like_instance = Likes.objects.get(user=User.objects.get(pk=request.user.id), liked=post)

        # Current user dislikes the post
        like_instance.delete()
        post.likes = post.likes - 1
        action = 'disliking'

    except:
        # User likes the post
        new_like = Likes.objects.create(user=User.objects.get(pk=request.user.id), liked=post)
        post.likes = post.likes + 1

        # Save changes
        new_like.save()
        action = 'liking'

    post.save()

    return JsonResponse({"quantity_of_likes": post.likes, "user_is": action})


@csrf_exempt
@login_required
def edit(request, post_id):
    
    # Check to see who's sending the form
    if request.user.id is not Post.objects.get(pk=post_id).creator.id:
        return HttpResponse('You are not allowed to make this operation.')

    # Check the method request
    if request.method != "PUT":
        return HttpResponse("You are using the wrong request method"), JsonResponse({"error": "Wrong method used in this route."})

    # Take the new content
    data = json.loads(request.body)

    try:
        # Update the content
        post = Post.objects.get(pk=post_id)
        if data.get("content") is None:
            return JsonResponse({"content": "is none"})
        else:
            post.content = data["content"]

        # Register the time that the content was changed
        post.updated_at = datetime.datetime.now()

        # Save changes
        post.save()

        return HttpResponse('everything went well', status=204)

    except Exception as error:
        return HttpResponse(error, status=204)


@csrf_exempt
@login_required
def alter_follow_state(request, person_id):
    
    # Check the method request
    if request.method != "PUT":
        return HttpResponse("You are using the wrong request method"), JsonResponse({"error": "Wrong method used in this route."})

    # PUT
    # if state exists, delete this record
    try:
        state = Following.objects.get(follower=User.objects.get(pk=request.user.id), following=User.objects.get(pk=person_id))
        state.delete()
    except:
        new_follow = Following.objects.create(follower=User.objects.get(pk=request.user.id), following=User.objects.get(pk=person_id))
        new_follow.save()

    