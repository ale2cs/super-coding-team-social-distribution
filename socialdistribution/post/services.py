import requests
from api.utils import create_basic_auth_header, validate_response

def get_posts_from_node(node, remote_author_id):
    response = requests.get(
            url=f"{remote_author_id}/posts",
            headers=create_basic_auth_header(node.username, node.password)
        )
    return validate_response(response)