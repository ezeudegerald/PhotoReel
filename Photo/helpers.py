

def context_args(request, args = None):
    if args is None:
        args = {}
    context = {}
    if request.user.is_authenticated:
        context['auth'] = 'true'
        context['user'] = request.user.username
    else:
        context['auth'] = 'false'
        context['user'] = ''
    return {**args, **context}

# def has_permission(self, request, view):
#     # Workaround to ensure DjangoModelPermissions are not applied
#     # to the root view when using DefaultRouter.
#     if getattr(view, '_ignore_model_permissions', False):
#         return True
#
#     if hasattr(view, 'get_queryset'):
#         queryset = view.get_queryset()
#     else:
#         queryset = getattr(view, 'queryset', None)
#
#     assert queryset is not None, (
#         'Cannot apply DjangoModelPermissions on a view that '
#         'does not set `.queryset` or have a `.get_queryset()` method.'
#     )
#
#     perms = self.get_required_permissions(request.method, queryset.model)
#
#     return (
#         request.user and
#         (request.user.is_authenticated() or not self.authenticated_users_only) and
#         request.user.has_perms(perms)
#     )