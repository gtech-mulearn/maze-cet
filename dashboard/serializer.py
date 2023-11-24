import uuid
from django.db.models import Q
from rest_framework import serializers

from utils.types import RoleTypes
from utils.utils import DateTimeUtils
from .models import User, TreasureLog, ScanLog


class UserRegisterSerializer(serializers.ModelSerializer):
    muid = serializers.CharField(required=False)
    image = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'fullname',
            'muid',
            'email',
            'phone',
            'image',
        ]

    def create(self, validated_data):
        validated_data['id'] = str(uuid.uuid4())
        validated_data['qr_code'] = str(uuid.uuid4())
        validated_data['is_active'] = True
        validated_data['created_at'] = DateTimeUtils.get_current_utc_time()

        return User.objects.create_user(**validated_data)


class UserTreasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreasureLog
        fields = []

    def create(self, validated_data):
        user_id = self.context.get('user_id')
        treasure = self.context.get('treasure')
        is_winner = self.context.get('is_winner')

        validated_data['id'] = str(uuid.uuid4())
        validated_data['treasure'] = treasure
        validated_data['user_id'] = user_id
        validated_data['is_claimed'] = is_winner
        validated_data['created_at'] = DateTimeUtils.get_current_utc_time()

        return TreasureLog.objects.create(**validated_data)


class UserDetailsSerializer(serializers.ModelSerializer):
    stalls_visited = serializers.SerializerMethodField()
    total_stalls = serializers.SerializerMethodField()
    scanned_users = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    image = serializers.CharField(allow_null=True)

    class Meta:
        model = User
        fields = [
            'role',
            'fullname',
            'scanned_users',
            'roles',
            'image'
        ]

    def get_scanned_users(self, obj):
        return ScanLog.objects.filter(Q(user1=obj) | Q(user2=obj)).count()

    def get_roles(self, obj):
        user1_scan_roles = ScanLog.objects.filter(user1=obj, user2__group__id=obj.group.id).values_list('user2__role',
                                                                                                        flat=True)
        user2_scan_roles = ScanLog.objects.filter(user2=obj, user1__group__id=obj.group.id).values_list('user1__role',
                                                                                                        flat=True)
        all_roles = set(list(user1_scan_roles) + list(user2_scan_roles) + [obj.role])
        user_roles_dict = {}
        for ro in RoleTypes.get_values():
            user_roles_dict[ro] = ro in all_roles
        return user_roles_dict


class UserQrCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('role', 'fullname')
