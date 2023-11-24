from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import User


class MuidBackend(ModelBackend):

    def authenticate(self, request, muid=None, **kwargs):
        try:
            user = User.objects.get(Q(muid=muid) | Q(email=muid))
        except User.DoesNotExist:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
