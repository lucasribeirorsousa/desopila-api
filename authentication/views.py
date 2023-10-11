from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework.permissions import IsAuthenticated

from checkout.models import Credit

from .utils import have_conditions_to_register_user

from .permissions import (
    UserPermissions
)
from .serializers import (
    HintUserSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    AuthSerializer,
    RefreshSerializer,
    UserUpdateSerializer,
)

from .models import User
from places.models import Address
from checkout.plugins import gateway

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [UserPermissions]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        try:
            conditions, errors = have_conditions_to_register_user(
                body=request.data,
            )

            if not conditions:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            raise ValidationError(error.args[0])

        address = request.data['address']
        address = Address.objects.create(**address)
        request.data['address'] = address.id

        return_data = super().create(request, *args, **kwargs)
        user = User.objects.get(email=request.data['email'])

        Credit.objects.create(user=user)
        gateway.create_customer(user=user, address=address)

        return return_data

    def list(self, request, *args, **kwargs):
        self.serializer_class = HintUserSerializer
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.serializer_class = UserUpdateSerializer
        
        return super().update(request, *args, **kwargs)


class AuthViewSet(TokenViewBase):
    serializer_class = AuthSerializer


class RefreshViewSet(TokenViewBase):
    serializer_class = RefreshSerializer


class ChangePasswordViewSet(UpdateAPIView):
    model = User
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return User.objects.get(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            check = user.check_password(
                serializer.data.get("old_password")
            )

            if not check:
                return Response(
                    {"old_password": "Senha errada."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.password = serializer.data.get("new_password")
            user.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
