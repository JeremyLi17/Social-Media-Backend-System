from rest_framework.permissions import BasePermission


# 要继承自BasePermission
class IsObjectOwner(BasePermission):
    """
    - 如果是 detail=False的action(URL里没有ID) 就只检测has_permission
    - 如果是 detail=True的action 就会同时检测has_permission和has_object_permission
    - 如果出错 默认的错误信息会显示 IsObjectOwner.message中的内容
    """
    message = 'You have no permission to access this object'

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
