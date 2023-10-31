from rest_framework.test import APITestCase
from social.models import Follower, Profile
from django.contrib.auth.models import User

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

    def test_get_followers(self):
        """
        Test GET request for followers of author_id
        """
        # check empty
        
        response = self.client.get(f'/service/authors/{self.user1_profile.id}/followers')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data, [])

        # user2 follows user1; user1 has user2 as a follower
        self.user2_follow.following.add(self.user1_profile)
        response = self.client.get(f'/service/authors/{self.user1_profile.id}/followers')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        user_id = response_data[0]['user']
        self.assertEqual(user_id, self.user2.id)
        

    def test_get_followers_action(self):
        """
        Test GET request checking if foreign_id follows author_id
        """
        # not following
        response = self.client.get(f'/service/authors/{self.user1_profile.id}/followers/{self.user2_profile.id}')
        response_data = response.json()
        is_follower = response_data['is_follower']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(is_follower, False)

        # user2 follows user1; user1 has user2 as a follower
        self.user2_follow.following.add(self.user1_profile)
        response = self.client.get(f'/service/authors/{self.user1_profile.id}/followers/{self.user2_profile.id}')
        response_data = response.json()
        is_follower = response_data['is_follower']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(is_follower, True)
 

    def test_put_followers_action(self):
        """
        Test PUT request making foreign_id follow author_id
        """
        # user2 follow user 1
        response = self.client.put(f'/service/authors/{self.user1_profile.id}/followers/{self.user2_profile.id}')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        following_message = response_data['message']
        self.assertEqual(self.user2_follow.following.all()[0], self.user1_profile)
        self.assertEqual(following_message, 'Now following.')

        # user2 attempts follow user1 again
        # not able to follow again
        response = self.client.put(f'/service/authors/{self.user1_profile.id}/followers/{self.user2_profile.id}')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        following_message = response_data['message']
        self.assertEqual(self.user2_follow.following.all()[0], self.user1_profile)
        self.assertEqual(following_message, 'Already following.')


    def test_delete_followers_action(self):
        """
        Test DELETE request making foreign_id unfollow author_id
        """
        # user2 follows user1
        self.user2_follow.following.add(self.user1_profile)

        # user2 unfollows user1
        response = self.client.delete(f'/service/authors/{self.user1_profile.id}/followers/{self.user2_profile.id}')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        following_message = response_data['message']
        self.assertEqual(len(self.user2_follow.following.all()), 0)
        self.assertEqual(following_message, 'Now unfollowed')

        # user2 attempts unfollow user1
        # not able to unfollow again
        response = self.client.delete(f'/service/authors/{self.user1_profile.id}/followers/{self.user2_profile.id}')
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