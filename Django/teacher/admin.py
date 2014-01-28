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
    
    def app_index(self, request, app_label, extra_context=None):
        user = request.user
        has_module_perms = user.has_module_perms(app_label)
        app_dict = {}
        for model, model_admin in self._registry.items():
            if app_label == model._meta.app_label:
                if has_module_perms:
                    perms = model_admin.get_model_perms(request)

                    # Check whether user has any perm for this module.
                    # If so, add the module to the model_list.
                    if True in perms.values():
                        info = (app_label, model._meta.model_name)
                        model_dict = {
                            'name': capfirst(model._meta.verbose_name_plural),
                            'object_name': model._meta.object_name,
                            'perms': perms,
                        }
                        if perms.get('change', False):
                            try:
                                model_dict['admin_url'] = reverse('%s_%s_changelist' % info, current_app=self.name)
                            except NoReverseMatch:
                                pass
                        if perms.get('add', False):
                            try:
                                model_dict['add_url'] = reverse('%s_%s_add' % info, current_app=self.name)
                            except NoReverseMatch:
                                pass
                        if app_dict:
                            app_dict['models'].append(model_dict),
                        else:
                            # First time around, now that we know there's
                            # something to display, add in the necessary meta
                            # information.
                            app_dict = {
                                'name': app_label.title(),
                                'app_label': app_label,
                                'app_url': '',
                                'has_module_perms': has_module_perms,
                                'models': [model_dict],
                            }
        if not app_dict:
            raise Http404('The requested admin page does not exist.')
        # Sort the models alphabetically within each app.
        app_dict['models'].sort(key=lambda x: x['name'])
        context = {
            'title': _('%s administration') % capfirst(app_label),
            'app_list': [app_dict],
        }
        context.update(extra_context or {})

        return TemplateResponse(request, self.app_index_template or [
            '%s/app_index.html' % app_label,
            '/app_index.html'
        ], context, current_app=self.name)
    
    # def get_urls(self):
        # from django.conf.urls import patterns, url

        # urls = super(UserAdmin, self).get_urls()
        # urls += patterns('',
            # url(r'^/$', self.admin_view(admin.add))
        # )
        # return urls
 
 
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



