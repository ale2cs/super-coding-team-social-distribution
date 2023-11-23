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