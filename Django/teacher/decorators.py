from functools import wraps
from django.utils.translation import ugettext as _
#from django.contrib.auth.views import login
from django.contrib.auth import REDIRECT_FIELD_NAME
from teacher.forms import UserAdminAuthenticationForm
from teacher.views import login


def user_login_required(view_func):
    """
    Decorator for views that checks that the user is logged in, 
    displaying the login page if necessary.
    """
    @wraps(view_func)
    def _checklogin(request, *args, **kwargs):
        if request.user.is_active:
            # The user is valid. Continue to the admin page.
            return view_func(request, *args, **kwargs)

        assert hasattr(request, 'session'), "The Django admin requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        defaults = {
            'template_name': 'admin/userLogin.html',
            'authentication_form': UserAdminAuthenticationForm,
            'extra_context': {
                'title': _('Log in'),
                'app_path': request.get_full_path(),
                REDIRECT_FIELD_NAME: request.get_full_path(),
            },
        }
        return login(request, **defaults)
    return _checklogin

