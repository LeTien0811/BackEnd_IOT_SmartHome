from rest_framework import permissions

class IsDeviceAdminOrMemberReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        user_roles = request.auth.get('role', {}) if request.auth else {}
        home_id_str = str(obj.home.home)
        user_role_in_home = user_roles.get(home_id_str)

        if request.method in permissions.SAFE_METHODS:
            # GET HEAD  OPPTIONS for all user.
            return user_role_in_home in ['ADMIN', 'MEMBER']

        # only put post delete if user role is ADMIN
        return user_role_in_home == 'ADMIN'