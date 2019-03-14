from rest_framework.permissions import IsAuthenticated


class IsReviewer(IsAuthenticated):

    def has_permission(self, request, view):
        return super(IsReviewer, self).has_permission(request, view) and request.user.reviewer
