import requests
from api.utils import create_basic_auth_header, validate_response
from api.serializers import ProfileSerializer, PostSerializer
from api.services import get_remote_node

def get_post_from_node(node, remote_post_id):
    try:
        response = requests.get(
                url=f"{remote_post_id}",
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token)
            )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}
    
def get_posts_from_node(node, remote_author_id):
    try:
        url = f"{remote_author_id}/posts"
        if node.name == 'A-Team':
            url = url + '/'
        response = requests.get(
                url=url,
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token)
            )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def get_image_from_node(node, remote_post_id):
    try:
        response = requests.get(
                url=f"{remote_post_id}/image",
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token)
            )
        if response.status_code == 404:
            return {'image': ''}
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def get_comments_from_node(node, remote_post_id):
    try:
        url = f"{remote_post_id}/comments"
        if node.name == 'A-Team':
            url = url + '/'
        response = requests.get(
                url = url,
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token)
            )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def get_likes_from_node(node, remote_post_id):
    try:
        url = f"{remote_post_id}/likes"
        if node.name == 'A-Team':
            url = url + '/'
        response = requests.get(
                url=url,
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token)
            )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def send_like_to_node(node, remote_post, request):
    try:
        remote_author_id = remote_post.split('/')[4]
        remote_post_id = remote_post.split('/')[6]

        if node.name == 'A-Team':
            url = f'{node.url}/authors/{remote_author_id}/posts/{remote_post_id}/likes/'
        else:
            url = f'{node.url}/authors/{remote_author_id}/inbox'
        author = request.user.profile
        serializer = ProfileSerializer(author, context={'request': request})
        if node.name == 'A-Team':
            json_data = {
                "author_id": serializer.data['id'].split('/')[-1]
            }
        else:
            json_data = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "summary": f"{author.user.username} likes your post",         
                "type": "like",
                "author": serializer.data,
                "object": remote_post
            }
        response = requests.post(
            url=url,
            headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token),
            json=json_data,

        )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def send_comment_to_node(node, comment, remote_post, request):
    try:
        remote_author_id = remote_post.split('/')[4]
        remote_post_id = remote_post.split('/')[6]

        if node.name == 'A-Team':
            url = f'{node.url}/authors/{remote_author_id}/posts/{remote_post_id}/comments/'
        else:
            url = f'{node.url}/authors/{remote_author_id}/inbox'
        author = request.user.profile
        serializer = ProfileSerializer(author, context={'request': request})
        if node.name == 'A-Team':
            json_data = {
                "author_id": serializer.data['id'].split('/')[-1],
                "contentType": 'text/plain',
                "comment": comment.content
            }
        else:
            json_data = {
                "type": "comment",
                "author": serializer.data,
                "comment": comment.content,
                "contentType": comment.contentType, 
                "published": comment.published,
                "id": remote_post
            }
        response = requests.post(
            url=url,
            headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token),
            json=json_data,

        )
        #print(response)
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}
    
def send_remote_post_to_node(node, remote_post_url, friend_id, request):
    try:
        # get remote post
        response = requests.get(
            url=remote_post_url,
            headers=create_basic_auth_header(node.outbound_username, node.outbound_password)
        )
        data = validate_response(response)
        data['source'] = request.build_absolute_uri('/')

        # send to inbox
        remote_author_id = friend_id.split('/')[4]
        response = requests.post(
            url=f'{node.url}/authors/{remote_author_id}/inbox', 
            headers=create_basic_auth_header(node.outbound_username, node.outbound_password),
            json=data
        )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}
    
def send_local_post_to_node(local_post, friend_id, request):
    try:
        # serialize local post
        serializer = PostSerializer(local_post, context={'request': request})
        node = get_remote_node(friend_id)

        # send to inbox
        remote_author_id = friend_id.split('/')[4]
        response = requests.post(
            url=f'{node.url}/authors/{remote_author_id}/inbox', 
            headers=create_basic_auth_header(node.outbound_username, node.outbound_password),
            json=serializer.data
        )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}