import base64
from drf_yasg import openapi
from rest_framework import serializers

def get_field_type(field):
    if isinstance(field, serializers.SerializerMethodField):
        return openapi.TYPE_STRING
    if isinstance(field, serializers.CharField):
        return openapi.TYPE_STRING
    elif isinstance(field, serializers.IntegerField):
        return openapi.TYPE_INTEGER
    elif isinstance(field, serializers.BooleanField):
        return openapi.TYPE_BOOLEAN
    return openapi.TYPE_STRING

def create_basic_auth_header(username, password):
    credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
    return {'Authorization': f'Basic {credentials}'}
