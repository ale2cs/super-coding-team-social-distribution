from datetime import timedelta
import json
import uuid
from django.db import transaction
from rest_framework.test import APITestCase
from social.models import Post, Profile
from django.contrib.auth.models import User
from django.utils import timezone

mock_post_data = {
    'title': 'NEW title',
    'id': 'id',
    'source': 'NEW source',
    'origin': 'NEW origin',
    'description': 'NEW description',
    'contentType': 'text/markdown',
    'content': 'new content',
    'author': {
        "type":"author",
        "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
        "host":"http://127.0.0.1:5454/",
        "displayName":"Lara Croft",
        "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
        "github": "http://github.com/laracroft",
        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
    },
    "visibility": "PUBLIC",
    "unlisted": False,
}

class PostApiTest(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(username='test', password='#password1234', email='test@test.com')
        self.profile = Profile.objects.get(user=self.user)
        self.post = Post.objects.create(
            title='title',
            id='id',
            source='source',
            origin='origin',
            description='description',
            contentType='text/plain',
            content='content',
            author=self.profile
        )

    def test_should_GET_post_detail(self):
        """Test the GET request for getting a single Post whose ID is POST_ID"""
        response = self.client.get(f'/service/authors/{self.profile.id}/posts/{self.post.id}')
        self.assertEqual(response.status_code, 201)

    def test_should_return_404_GET_post_detail(self):
        """Test the GET request returns 404 for getting a single Post whose ID is POST_ID"""
        response = self.client.get(f'/service/authors/{self.profile.id}/posts/{uuid.uuid4}')
        self.assertEqual(response.status_code, 404)

    def test_should_POST_updates_to_post_detail(self):
        """Test POST request for updating a single Post whose ID is POST_ID"""
        response = self.client.post(f'/service/authors/{self.profile.id}/posts/{self.post.id}', 
                                    json.dumps(mock_post_data), 
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        self.post.refresh_from_db()
        self.assertEqual(self.post.title, mock_post_data['title'])
        self.assertEqual(self.post.id, mock_post_data['id'])
        self.assertEqual(self.post.source, mock_post_data['source'])
        self.assertEqual(self.post.origin, mock_post_data['origin'])
        self.assertEqual(self.post.description, mock_post_data['description'])
        self.assertEqual(self.post.contentType, mock_post_data['contentType'])
        self.assertEqual(self.post.content, mock_post_data['content'])
        self.assertEqual(self.post.visibility, mock_post_data['visibility'])
        self.assertEqual(self.post.unlisted, mock_post_data['unlisted'])

    def test_should_return_404_POST_post_detail(self):
        """Test POST request returns 404 for getting a post_id which does not exist"""
        response = self.client.post(f'/service/authors/{self.profile.id}/posts/{uuid.uuid4}', 
                                    json.dumps(mock_post_data), 
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_should_DELETE_post_detail(self):
        """Test DELETE request should delete post"""
        response = self.client.delete(f'/service/authors/{self.profile.id}/posts/{self.post.id}')
        self.assertEqual(response.status_code, 200)
        try:
            post = Post.objects.get(id=self.post.id)
        except:
            post = None
        self.assertIsNone(post)

    def test_should_return_404_DELETE_post_detail(self):
        """Test DELETE request should return 404"""
        response = self.client.delete(f'/service/authors/{self.profile.id}/posts/{uuid.uuid4}')
        self.assertEqual(response.status_code, 404)

    def test_should_PUT_post_detail(self):
        """Test PUT request should put a new post with post_id as the id"""
        post_id = 'newID123'
        response = self.client.put(f'/service/authors/{self.profile.id}/posts/{post_id}', 
                                   json.dumps(mock_post_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)

        try:
            post = Post.objects.get(id=post_id)
        except:
            post = None

        self.assertIsNotNone(post)
        self.assertEqual(post.id, post_id)
        self.assertEqual(post.title, mock_post_data['title'])
        self.assertEqual(post.source, mock_post_data['source'])
        self.assertEqual(post.origin, mock_post_data['origin'])
        self.assertEqual(post.description, mock_post_data['description'])
        self.assertEqual(post.contentType, mock_post_data['contentType'])
        self.assertEqual(post.content, mock_post_data['content'])
        self.assertEqual(post.visibility, mock_post_data['visibility'])
        self.assertEqual(post.unlisted, mock_post_data['unlisted'])
        
    def test_should_return_400_PUT_post_detail_integrityError(self):
        """Test PUT request should return 400 error when trying to PUT an already existing post_id"""
        post_id = 'newID1234'
        Post.objects.create(
            title='title',
            id=post_id,
            source='source',
            origin='origin',
            description='description',
            contentType='text/plain',
            content='content',
            author=self.profile
        )
        
        with transaction.atomic():
            response = self.client.put(f'/service/authors/{self.profile.id}/posts/{post_id}', 
                                   json.dumps(mock_post_data),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 400)
            
    def test_should_GET_post_list(self):
        """Test GET request for post list returns list ordered by most recent descending"""
        with transaction.atomic():
            Post.objects.create(
                title='title',
                id='oldId123',
                source='source',
                origin='origin',
                description='description',
                contentType='text/plain',
                content='content',
                author=self.profile,
                published=timezone.now()-timedelta(days=360)
            )
            response = self.client.get(f'/service/authors/{self.profile.id}/posts')
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertGreater(response_data[0]['published'], response_data[1]['published'])
        
    def test_should_return_400_for_invalid_query_param_GET_post_list(self):
        """Test GET request to return status code 400 when an invalid query param is sent"""
        with transaction.atomic():
            response = self.client.get(f'/service/authors/{self.profile.id}/posts?page=1&size=0')
            self.assertEqual(response.status_code, 400)
            response = self.client.get(f'/service/authors/{self.profile.id}/posts?page=test')
            self.assertEqual(response.status_code, 400)
            response = self.client.get(f'/service/authors/{self.profile.id}/posts?page=1&size=test')
            self.assertEqual(response.status_code, 400)
            
    def test_should_paginate_GET_post_list(self):
        """Test GET request to return a paginated list of posts"""
        with transaction.atomic():
            Post.objects.create(
                title='title',
                id='oldId123',
                source='source',
                origin='origin',
                description='description',
                contentType='text/plain',
                content='content',
                author=self.profile,
                published=timezone.now()-timedelta(days=360)
            )
            response = self.client.get(f'/service/authors/{self.profile.id}/posts?page=1&size=1')
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertEqual(len(response_data), 1)
            
    def test_should_POST_post_list(self):
        """Test POST request to create a new post with a system generated id"""
        response = self.client.post(f'/service/authors/{self.profile.id}/posts',
                                    json.dumps(mock_post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
    def tearDown(self):
        self.user.delete()
        self.profile.delete()
        self.post.delete()