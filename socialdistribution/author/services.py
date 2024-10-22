import requests
from api.utils import create_basic_auth_header, validate_response

def get_authors_from_node(node):
    try:
        url = f'{node.url}/authors'
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
    

def get_author_from_node(node, url):
    try:
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

def get_following_from_node(node, author_id, remote_author_id):
    try:
        url = f"{remote_author_id}/followers/{author_id}"
        if node.name == 'A-Team':
            url = url + '/'
        response = requests.get(
                url=url,
                headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token)
            )
        if node.name == 'A-Team' and response.status_code in [404, 400]:
            result = {'is_follower': False}
        elif node.name == 'A-Team' and response.status_code == 200:
             result = {'is_follower': True}
        else:
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
            url = f"{remote_author_id}/followRequests/"
        else:
            url = f"{remote_author_id}/inbox"

        response = requests.post(
            url=url, 
            headers=create_basic_auth_header(node.outbound_username, node.outbound_password, node.token),
            json=data
        )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node {node.url}: {e}")
        return {}