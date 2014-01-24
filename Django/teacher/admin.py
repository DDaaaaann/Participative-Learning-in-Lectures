from django.contrib import admin
from django.contrib.admin.sites import AdminSite
 
from teacher.forms import UserAdminAuthenticationForm
from teacher.views import profile_page
 
class UserAdmin(AdminSite):
    # Anything we wish to add or override
    
    login_form = UserAdminAuthenticationForm
    login_template = 'admin/userLogin.html'
    #index_template = 'teacher/profilepage.html'
    
    def index(self, request):
        return profile_page(request)
    
    def has_permission(self, request):
        """
        Removed check for is_staff.
        """
        return request.user.is_active
 
user_admin_site = UserAdmin(name='usersadmin')
# Run user_admin_site.register() for each model we wish to register
# for our admin interface for users
 
# Run admin.site.register() for each model we wish to register
# with the REAL django admin!



