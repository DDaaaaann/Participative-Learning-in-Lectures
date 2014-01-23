from django.contrib import admin
from django.contrib.admin.sites import AdminSite
 
from teacher.forms import UserAdminAuthenticationForm
 
class UserAdmin(AdminSite):
    # Anything we wish to add or override
    
    login_form = UserAdminAuthenticationForm
    login_template = 'admin/userLogin.html'
    index_template = 'teacher/profilepage.html'
    
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



