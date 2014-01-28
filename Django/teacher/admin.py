from django.contrib import admin
from django.contrib.admin.sites import AdminSite
 
from teacher.forms import UserAdminAuthenticationForm, AdminAuthenticationForm
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
    
    

 
class Admin(AdminSite):
    
    login_form = AdminAuthenticationForm
    
    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser
 
 
user_admin_site = UserAdmin(name='usersadmin')
# Run user_admin_site.register() for each model we wish to register
# for our admin interface for users
 
# Run admin.site.register() for each model we wish to register
# with the REAL django admin!
admin.site = Admin(name='admin')



