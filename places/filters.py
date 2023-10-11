from rest_framework.filters import BaseFilterBackend

class LocalTypeFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        local_type = request.GET.getlist('local_type')

        if not local_type:
            return queryset.all()
        else:
            try:
                return queryset.filter(local_type__in=local_type)
            except Exception:
                return queryset.none()

class UserFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.query_params.get('user', None)

        if not user:
            return queryset.all()
        else:
            try:
                return queryset.filter(user=user)
            except Exception:
                return queryset.none()

class StatusFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        status = request.query_params.get('status', None)

        if not status:
            return queryset.all()
        else:
            try:
                return queryset.filter(status=status)
            except Exception:
                return queryset.none()
