import base64
from drf_yasg import openapi
from rest_framework import serializers
from rest_framework.response import Response

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

def validate_paginator_parameters(size, page):
    if size is not None and not size.isdigit():
        return {'error': "Invalid Query Parameter: Size = 0"}, 400
    elif size == '0':
        return {'error': f"Invalid Query Parameter: Size '{size}'"}, 400

    if page is not None and not page.isdigit():
        return {'error': f"Invalid Query Parameter: Page '{page}'"}, 400

    return None, None
  
def create_basic_auth_header(username, password):
    credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
    return {'Authorization': f'Basic {credentials}'}
