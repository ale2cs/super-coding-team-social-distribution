import requests
from api.utils import create_basic_auth_header, validate_response
from api.serializers import ProfileSerializer

def get_posts_from_node(node, remote_author_id):
    try:
        response = requests.get(
                url=f"{remote_author_id}/posts",
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password)
            )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def get_image_from_node(node, remote_post_id):
    try:
        response = requests.get(
                url=f"{remote_post_id}/image",
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password)
            )
        if response.status_code == 404:
            return {'image': ''}
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def get_comments_from_node(node, remote_post_id):
    try:
        response = requests.get(
                url=f"{remote_post_id}/comments",
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password)
            )
        print(response.json())
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def get_likes_from_node(node, remote_post_id):
    try:
        response = requests.get(
                url=f"{remote_post_id}/likes",
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password)
            )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def send_like_to_node(node, remote_post, request):
    try:
        remote_author_id = remote_post.split('/')[4]
        author = request.user.profile
        serializer = ProfileSerializer(author, context={'request': request})
        json_data = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "summary": f"{author.user.username} likes your post",         
            "type": "like",
            "author": serializer.data,
            "object": remote_post
        }
        response = requests.post(
            url=f'{node.url}/authors/{remote_author_id}/inbox', 
            headers=create_basic_auth_header(node.outbound_username, node.outbound_password),
            json=json_data,

        )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def send_comment_to_node(node, comment, remote_post, request):
    try:
        remote_author_id = remote_post.split('/')[4]
        author = request.user.profile
        serializer = ProfileSerializer(author, context={'request': request})
        json_data = {
            "type": "comment",
            "author": serializer.data,
            "comment": comment.content,
            "contentType": comment.contentType, 
            "published": comment.published,
            "id": remote_post
        }
        response = requests.post(
            url=f'{node.url}/authors/{remote_author_id}/inbox', 
            headers=create_basic_auth_header(node.outbound_username, node.outbound_password),
            json=json_data,

        )
        print(response)
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}