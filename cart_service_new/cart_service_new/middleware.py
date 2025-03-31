from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions

class NoDBJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Override get_user to return a dummy user or None, skipping database lookup.
        We’ll use the token payload directly in views.
        """
        try:
            # Return a dummy user object with data from the token
            class DummyUser:
                def __init__(self, token):
                    self.id = token.get('user_id')
                    self.username = token.get('username', 'anonymous')
                    self.email = token.get('email')
                    self.role = token.get('role', 'user')

                def __str__(self):
                    return self.username

            return DummyUser(validated_token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"User cannot be identified: {str(e)}")