from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Following, Likes
from .forms import postForm

import json
import datetime


def index(request):
    allposts = Post.objects.all().order_by('-created_at')
    return render(request, "network/index.html", {
        'posts': allposts
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

    return render(request, "network/profile.html", {
        'creator': User.objects.get(id=profile_user_id).username,
        'followers': followers,
        'following': following,
        'all_user_posts': all_user_posts,
        'user_is_the_profile_owner': request.user.id == profile_id
    })


@login_required
def content_following(request):

    # All users that the current user follow
    all_users_beeing_followed_by_current_user = Following.objects.filter(follower=request.user.id).values()
    posts = []
    for followed_user in all_users_beeing_followed_by_current_user:
        bunch_of_posts = Post.objects.filter(creator=followed_user['id']).order_by('-created_at')[:10]
        for post in bunch_of_posts:
            posts.append(post)

    return render(request, "network/following.html", {
        'posts': posts,
    })


@login_required
def returning_post_data_as_json(request):
    pass


@login_required
def user_liking_or_unliking(request, post_id):
    # Number of current post likes    
    quantity_likes = Likes.objects.filter(liked= Post.objects.get(pk=post_id)).count() # I have a problem here
    return HttpResponse(quantity_likes)

    # Update the number of likes
    if len(Likes.objects.get(user=User.objects.get(pk=request.user.id), likes=post_id)) > 0:
        return JsonResponse({"action": "unliking", "likes": quantity_likes - 1})
    
    return JsonResponse({"action": "liking", "likes": quantity_likes + 1})


@csrf_exempt
@login_required
def likes(request, post_id):
    
    # Dinamiclly, like or unlike a post
    if request.method != 'PUT':
        return JsonResponse({"error": "Wrong method used in this route."})

    data = json.loads(request.body)

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Take a reference and all data from the found post
    post = Post.objects.get(id=post_id)

    # Check if the user has already liked this post
    try:
        like_instance = Likes.objects.get(user=request.user.id, liked=post_id)

        # Current user dislikes the post
        like_instance.delete()

        # Save changes
        like_instance.save()

    except:
        # User likes the post
        new_like = Likes.objects.create(user=User.objects.get(pk=request.user.id), liked=post)

        # Save changes
        new_like.save()

    # Update the quantity of likes
    post.likes = data.get("likes")
    post.save()

    return JsonResponse(post.all_data())


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
        if data.get("content") is not None:
            post.content = data["content"]

        # Register the time that the content was changed
        post.updated_at = datetime.datetime.now()

        # Save changes
        post.save()

        return JsonResponse({'message': 'everything went well'})

    except Exception as error:
        return JsonResponse({'message': 'something went badly', 'error': error})

