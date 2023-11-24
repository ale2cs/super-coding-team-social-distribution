import requests
from api.utils import create_basic_auth_header

def get_authors_from_node(node):
    response = requests.get(
            url=f"{node.url}/service/authors",
            headers=create_basic_auth_header(node.username, node.password)
        )
    return response.json()

def get_author_from_node(node, url):
    response = requests.get(
        url=url,
        headers=create_basic_auth_header(node.username, node.password)
    )
    return response.json()

def get_following_from_node(node, author_id, remote_author_id):
    response = requests.get(
            url=f"{remote_author_id}/followers/{author_id}",
            headers=create_basic_auth_header(node.username, node.password)
        )
    return response.json()

def put_follower_into_node(node, author_id, remote_author_id):
    response = requests.put(
        url=f"{remote_author_id}/followers/{author_id}",
        headers=create_basic_auth_header(node.username, node.password)
    )
    return response.json()
    
def delete_follower_from_node(node, author_id, remote_author_id):
    response = requests.delete(
        url=f"{remote_author_id}/followers/{author_id}",
        headers=create_basic_auth_header(node.username, node.password)
    )
    return response.json()
