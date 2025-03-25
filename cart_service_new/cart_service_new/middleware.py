import jwt
from django.http import JsonResponse
from functools import wraps

SECRET_KEY = "django-insecure-rsnl*nk(+yo+0*w#9@sgxbih5pi(ethaj4%r$7d%@bt!!mvyts"

# class JWTAuthMiddleware:
#     """ Middleware to verify JWT locally """
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         token = request.headers["Authorization"]
#         if not token or not token.startswith("Bearer "):
#             return JsonResponse({"error": "Unauthorized"}, status=401)

#         token = token.split(" ")[1]
#         try:
#             decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#             request.user = decoded_token  # Attach user data
#         except jwt.ExpiredSignatureError:
#             return JsonResponse({"error": "Token expired!"}, status=401)
#         except jwt.InvalidTokenError:
#             return JsonResponse({"error": "Invalid token!"}, status=401)

#         return self.get_response(request)

def token_required(view_func):
    """ Decorator to check JWT token """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = None


        # Debug: Print Authorization Header
        print("Authorization Header:", request.META.get('HTTP_AUTHORIZATION'))
        # Get token from headers (Django uses HTTP_AUTHORIZATION)
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]

        if not token:
            return JsonResponse({"message": "Token is missing!"}, status=401)

        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print("✅ Decoded Token:", decoded_token)
            request.user_data = decoded_token  # Store in request object
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token expired!"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid token!"}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view

def admin_required(view_func):
    """ Decorator to check if the user is an admin """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.headers.get('Authorization')

        if not token or not token.startswith('Bearer '):
            return JsonResponse({"message": "Token is missing!"}, status=401)

        try:
            decoded_token = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])
            request.META["user"] = decoded_token

            if decoded_token.get("role") != "admin":
                return JsonResponse({"message": "Admins only!"}, status=403)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token expired!"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid token!"}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view
