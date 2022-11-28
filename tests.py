from django.test import TestCase
from .models import User, Post, Following, Likes
from datetime import datetime

# Create your tests here.
class TestAll(TestCase):

    def setUp(self):

        # Create some users
        user1 = User.objects.create(username='test1')
        user2 = User.objects.create(username='test2')
        user3 = User.objects.create(username='test3')

        # Create Posts
        post1 = Post.objects.create(creator=user1, content='simple post', created_at=datetime(2022,11,23,16,39,40), updated_at=datetime(2022,11,23,16,40,30), likes=0)
        post2 = Post.objects.create(creator=user2, content='meoow', created_at=datetime(2022,11,23,16,41,40), updated_at=datetime(2022,11,23,16,42,50), likes=0)
        post3 = Post.objects.create(creator=user3, content='can we be?', created_at=datetime(2022,11,23,16,43,55), updated_at=datetime(2022,11,23,16,43,55), likes=0)

        # Create Following
        following1 = Following.objects.create(follower=user1, following=user1)
        following2 = Following.objects.create(follower=user1, following=user3)
        following3 = Following.objects.create(follower=user1, following=user2)

        # Create Likes
        likes1 = Likes.objects.create(user=user2, liked=post1)
        likes2 = Likes.objects.create(user=user3, liked=post2)
        likes3 = Likes.objects.create(user=user2, liked=post3)

    def testPost1(self):
        """This is a valid post"""
        firstPost = Post.objects.get(content='simple post')
        self.assertTrue(firstPost.is_valid())
    
    def testPost2(self):
        """This is a valid post"""
        secondPost = Post.objects.get(content='can we be?')
        self.assertTrue(secondPost.is_valid())

    def testPost3(self):
        """This is a valid post"""
        thirdPost = Post.objects.get(content='meoow')
        self.assertTrue(thirdPost.is_valid())

    
    def testFollowing1(self):
        """This is an invalid following"""
        firstFollowing = Following.objects.get(following=User.objects.get(username='test1'))
        self.assertFalse(firstFollowing.is_valid())

    def testFollowing2(self):
        """This is a valid following"""
        secondFollowing = Following.objects.get(following=User.objects.get(username='test3'))
        self.assertTrue(secondFollowing.is_valid())

    def testFollowing3(self):
        """This is a valid following"""
        thirdFolowing = Following.objects.get(following=User.objects.get(username='test2'))
        self.assertTrue(thirdFolowing.is_valid())


    def testLikes1(self):
        """The liking of a user to a post happens normally"""
        firstLike = Likes.objects.get(liked=Post.objects.get(content='simple post'))
        self.assertTrue(firstLike.is_valid())

    def testLikes2(self):
        """The liking of a user to a post happens normally"""
        secodLike = Likes.objects.get(liked=Post.objects.get(content='meoow'))
        self.assertTrue(secodLike.is_valid())

    def testLikes3(self):
        """The liking of a user to a post happens normally"""
        thirdLike = Likes.objects.get(liked=Post.objects.get(content='can we be?'))
        self.assertTrue(thirdLike.is_valid())