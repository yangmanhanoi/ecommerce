from django.test import TestCase

# Create your tests here.
import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken

def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}
    
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQwNDk5OTU5LCJpYXQiOjE3NDA0OTYzNTksImp0aSI6IjBlNzkwYWY3MzMxMDQ3YWJiNTZjYjM0MmNlZDczN2U4IiwidXNlcl9pZCI6NCwidXNlcm5hbWUiOiJ0ZXN0X3NpZ25fdXBfMyIsImVtYWlsIjoibmFtX3Rlc3Rfc2lnbl91cF8zQGV4YW1wbGUuY29tIiwicGhvbmVOdW1iZXIiOiIxMjM0NTY3ODMzIiwiaW1hZ2VVcmwiOiJodHRwczovL3RzZTEubW0uYmluZy5uZXQvdGg_aWQ9T0lQLmtRWDhiVEJRYV9OMEp2UzhTVm9wdEFIYUU3JnBpZD1BcGkmUD0wJmg9MTgwIiwicm9sZSI6InVzZXIifQ.CiDE-WDsbtn0vJxOtB7K_OcOi1R3ly9RWWxWzb5Q_bc'
claims = decode_jwt(token=token)
print(claims)
