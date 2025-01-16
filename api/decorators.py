from functools import wraps
from django.http import JsonResponse

def post_required(f):
    @wraps(f)
    def decorated_function(req, *args, **kwargs):
        if req.method != 'POST':
            return JsonResponse({"error": "Invalid request method"}, status=405)
        return f(req, *args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(req, *args, **kwargs):
        if req.user.is_anonymous:
            print(req.user)
            return JsonResponse({"error": "Unauthorized"}, status=401)
        return f(req, *args, **kwargs)
    return decorated_function

def host_required(f):
    @wraps(f)
    @login_required
    def decorated_function(req, *args, **kwargs):
        if not req.user.is_host:
            return JsonResponse({"error": "Only hosts can create venues"}, status=403)
        return f(req, *args, **kwargs)
    return decorated_function