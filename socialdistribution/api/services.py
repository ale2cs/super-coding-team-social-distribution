import requests
from .utils import create_basic_auth_header, validate_response
from .models import Node

def get_author_from_link(author_link):
    try:
        nodes = Node.objects.all()
        for node in nodes:
            if node.url in author_link:
                response = requests.get(
                        url=author_link,
                        headers=create_basic_auth_header(node.outbound_username, node.outbound_password)
                    )
        return validate_response(response)
    except Exception as e:
        print(f"Error Connecting to node: {node.url} {e}")
        return {}