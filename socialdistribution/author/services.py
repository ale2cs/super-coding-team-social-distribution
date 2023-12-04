import requests
from api.utils import create_basic_auth_header, validate_response

def get_authors_from_node(node):
    try:
        print(node.name)
        if node.name == 'A-Team':
            response = requests.get(
                    url=f"{node.url}/authors/",
                    headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token)
                )

        else:
            response = requests.get(
                    url=f"{node.url}/authors",
                    headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token)
                )
        print(response.json())
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}
    

def get_author_from_node(node, url):
    try:
        response = requests.get(
            url=url,
            headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token)
        )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def get_following_from_node(node, author_id, remote_author_id):
    try:
        response = requests.get(
                url=f"{remote_author_id}/followers/{author_id}",
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token)
            )
        result = validate_response(response)
        if isinstance(result, bool):
                        result = {'is_follower': result}
        return result
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}

def post_following_to_node(node, remote_author_id, data):
    try:
        if node.name == 'A-Team':
            response = requests.post(
                url=f"{remote_author_id}/followRequests/",
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token),
                json=data
            )
        else:
            response = requests.post(
                url=f"{remote_author_id}/inbox",
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token),
                json=data
            )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node {node.url}: {e}")
        return {}