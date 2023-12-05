from rest_framework.test import APITestCase
from author.models import Follower, Profile
from django.contrib.auth.models import User
from api.models import Node
from api.utils import create_basic_auth_header

class FollowerAPITest(APITestCase):
    def setUp(self):
        # first user
        self.user1 = User.objects.create_user(username='user1', password='pass123$', email='user1@gmail.com')
        self.user1_profile = Profile.objects.get(user=self.user1)
        self.user1_follow = Follower.objects.get(profile=self.user1_profile)

        # second user
        self.user2 = User.objects.create_user(username='user2', password='pass123$', email='user2@gmail.com')
        self.user2_profile = Profile.objects.get(user=self.user2)
        self.user2_follow = Follower.objects.get(profile=self.user2_profile)
        
        self.node = Node.objects.create(
            name = 'node',
            url = 'http://localhost:8000',
            username = '123',
            password = '123'
        )

    def test_get_followers(self):
        """
        Test GET request for followers of author_id
        """
        # check empty
        
        response = self.client.get(f'/authors/{self.user1_profile.id}/followers', 
            headers=create_basic_auth_header(self.node.username, self.node.password))
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data, {'type': 'followers', 'items': []})

        # user2 follows user1; user1 has user2 as a follower
        self.user2_follow.following.add(self.user1_profile)
        response = self.client.get(f'/authors/{self.user1_profile.id}/followers', 
            headers=create_basic_auth_header(self.node.username, self.node.password))
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        user_id = response_data['items'][0]['id'].split('/')[-1]
        self.assertEqual(user_id, self.user2_profile.id)
        

    def test_get_followers_action(self):
        """
        Test GET request checking if foreign_id follows author_id
        """
        # not following
        response = self.client.get(f'/authors/{self.user1_profile.id}/followers/{self.user2_profile.id}', 
            headers=create_basic_auth_header(self.node.username, self.node.password))
        response_data = response.json()
        is_follower = response_data['is_follower']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(is_follower, False)

        # user2 follows user1; user1 has user2 as a follower
        self.user2_follow.following.add(self.user1_profile)
        response = self.client.get(f'/authors/{self.user1_profile.id}/followers/{self.user2_profile.id}', 
            headers=create_basic_auth_header(self.node.username, self.node.password))
        response_data = response.json()
        is_follower = response_data['is_follower']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(is_follower, False)

    def test_put_followers_action(self):
        """
        Test PUT request making foreign_id follow author_id
        """
        # user2 follow user 1
        response = self.client.put(f'/authors/{self.user1_profile.id}/followers/{self.user2_profile.id}', 
            headers=create_basic_auth_header(self.node.username, self.node.password))
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        following_message = response_data['message']
        self.assertEqual(following_message, 'Now following.')

    def test_delete_followers_action(self):
        """
        Test DELETE request making foreign_id unfollow author_id
        """
        # user2 follows user1
        self.user2_follow.following.add(self.user1_profile)

        # user2 unfollows user1
        response = self.client.delete(f'/authors/{self.user1_profile.id}/followers/{self.user2_profile.id}', 
            headers=create_basic_auth_header(self.node.username, self.node.password))
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        following_message = response_data['message']
        self.assertEqual(len(self.user2_follow.following.all()), 0)
        self.assertEqual(following_message, 'Now unfollowed')

        # user2 attempts unfollow user1
        # not able to unfollow again
        response = self.client.delete(f'/authors/{self.user1_profile.id}/followers/{self.user2_profile.id}', 
            headers=create_basic_auth_header(self.node.username, self.node.password))
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        following_message = response_data['message']
        self.assertEqual(len(self.user2_follow.following.all()), 0)
        self.assertEqual(following_message, 'Cannot unfollow, not following.')


    def tearDown(self):
        # delete first user
        self.user1.delete()
        self.user1_profile.delete()
        self.user1_follow.delete()

        # delete second user
        self.user2.delete()
        self.user2_profile.delete()
        self.user2_follow.delete()