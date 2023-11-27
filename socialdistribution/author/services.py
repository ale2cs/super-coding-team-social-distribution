import requests
from api.utils import create_basic_auth_header, validate_response

def get_authors_from_node(node):
    response = requests.get(
            url=f"{node.url}/authors",
            headers=create_basic_auth_header(node.outbound_username, node.outbound_password)
        )
    return validate_response(response)

def get_author_from_node(node, url):
    response = requests.get(
        url=url,
        headers=create_basic_auth_header(node.outbound_username, node.outbound_password)
    )
    return validate_response(response)

def get_following_from_node(node, author_id, remote_author_id):
    response = requests.get(
            url=f"{remote_author_id}/followers/{author_id}",
            headers=create_basic_auth_header(node.outbound_username, node.outbound_password)
        )
    result = validate_response(response)
    if isinstance(result, bool):
                    result = {'is_follower': result}
    return result

def post_following_to_node(node, remote_author_id, data):
    response = requests.post(
        url=f"{remote_author_id}/inbox",
        headers=create_basic_auth_header(node.outbound_username, node.outbound_password),
        json=data
    )
    return validate_response(response)
