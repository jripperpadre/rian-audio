import time

from django.contrib.auth import logout
from django.shortcuts import redirect

from .constants import SESSION_IDLE_TIMEOUT


class IdleTimeoutMiddleware:
    """
    Server-side idle timeout enforcement — staff/admin users only.

    Regular customers are NOT affected; their sessions follow the normal
    Django SESSION_COOKIE_AGE lifetime.

    For staff users, tracks the last-activity timestamp in the session.
    When idle for longer than SESSION_IDLE_TIMEOUT seconds, logs them out
    and redirects to the login page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only enforce idle timeout for staff/admin accounts
        if request.user.is_authenticated and request.user.is_staff:
            now = time.time()
            last_activity = request.session.get("last_activity")

            if last_activity is not None:
                idle_seconds = now - last_activity
                if idle_seconds > SESSION_IDLE_TIMEOUT:
                    logout(request)
                    response = redirect("login")
                    response.set_cookie(
                        "session_expired",
                        "1",
                        max_age=10,
                        samesite="Lax",
                    )
                    return response

            # Update last_activity on every request (sliding window)
            request.session["last_activity"] = now

        response = self.get_response(request)
        return response
