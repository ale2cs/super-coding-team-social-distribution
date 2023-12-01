import requests
from api.utils import create_basic_auth_header, validate_response

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