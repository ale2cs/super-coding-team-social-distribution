import base64
from django.http import HttpResponse
from .models import Node

class AuthMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.path.startswith('/service/'):
            auth_header = request.META.get('HTTP_AUTHORIZATION', b'')
            if not len(auth_header):
                return HttpResponse({"Unauthorized."}, status=401)
            
            token_type, _, credentials = auth_header.partition(' ')
            
            try:
                username, password = base64.b64decode(credentials).decode().split(':')
            except:
                return HttpResponse("Error decoding Authorization header", status=400)
            
            node = Node.objects.filter(username=username).first()
            
            if not node:
                return HttpResponse(f"Node of username '{username}' not found.", status=404)
            
            if not node.use_authentication or token_type == 'Basic' and node.password == password:
                return self.get_response(request)

            return HttpResponse({"Unauthorized."}, status=401)
        
        return self.get_response(request)
