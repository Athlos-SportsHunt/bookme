from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def host_required(f):
    @wraps(f)
    def decorated_function(req,*args, **kwargs):
        if not req.user.is_authenticated:
            messages.error(req, "You need to login first")
            return redirect('core:login')

        elif not req.user.is_host:
            messages.error(req, "You are not host")
            return redirect('core:index')
        
        return f(req,*args, **kwargs)
    return decorated_function
