import jwt
from django.http import JsonResponse

SECRET_KEY = "django-insecure-rsnl*nk(+yo+0*w#9@sgxbih5pi(ethaj4%r$7d%@bt!!mvyts"

class JWTAuthMiddleware:
    """ Middleware to verify JWT locally """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=401)

        token = token.split(" ")[1]
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = decoded_token  # Attach user data
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expired!"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token!"}, status=401)

        return self.get_response(request)