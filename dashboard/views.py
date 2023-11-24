import random
import random
import requests
import string
import uuid
from decouple import config
from django.contrib.auth import authenticate
from django.db.models import Case, When, Q, BooleanField, Count, Avg
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from dashboard.serializer import UserRegisterSerializer, \
    UserTreasureSerializer, UserDetailsSerializer, UserQrCodeSerializer
from utils.permission import TokenGenerate, CustomizePermission, JWTUtils
from utils.response import CustomResponse
from utils.types import RoleTypes
from utils.utils import DateTimeUtils
from .models import User, Treasures, SystemSettings, Group, TreasureLog, ScanLog

DOMAIN_NAME = config('DOMAIN_NAME')


def generate_random_words(num_words, word_length):
    words = []
    for _ in range(num_words):
        word = ''.join(random.choice(string.ascii_lowercase) for _ in range(word_length))
        words.append(word)
    return words


def allocate_group_and_roles(user_obj):
    TOTAL_GROUPS_LIMIT = int(SystemSettings.objects.filter(key='total_groups').first().value)
    MEMBER_COUNT = int(SystemSettings.objects.filter(key='member_count').first().value)

    while True:
        gp_number = random.randint(1, TOTAL_GROUPS_LIMIT)
        group_obj = Group.objects.filter(group_order=gp_number).first()

        if group_obj:
            if group_obj.member_count < MEMBER_COUNT:
                available_roles = set(RoleTypes.get_values())
                roles_available = set(User.objects.filter(group_id=group_obj.id).values_list("role", flat=True))
                filtered_roles = available_roles - roles_available
                role = random.choice(list(filtered_roles))
                group_obj.member_count += 1
                group_obj.save()
                user_obj.group = group_obj
                user_obj.role = role
                user_obj.save()
                break
        else:
            role = random.choice(RoleTypes.get_values())
            data = {
                'id': uuid.uuid4(),
                'title': generate_random_words(2, 3),
                'group_order': str(gp_number),
                'member_count': 1,
            }
            group = Group.objects.create(**data)
            user_obj.group = group
            user_obj.role = role
            user_obj.save()
            break


class UserRegisterAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user_obj = serializer.save()
            allocate_group_and_roles(user_obj)
            user = authenticate(self.request, muid=user_obj.email)
            auth = TokenGenerate().generate(user=user)
            return CustomResponse(response=auth).get_success_response()

        return CustomResponse(response=serializer.errors).get_failure_response()


class ConnectWithMuid(APIView):
    authentication_classes = [CustomizePermission]

    def post(self, request):
        user_id = JWTUtils.fetch_user_id(request)

        muid = request.data.get('muid').lower()
        password = request.data.get('password')
        URL = DOMAIN_NAME + '/api/v1/auth/connect-with-muid/'
        response = requests.post(URL, data={'emailOrMuid': muid, 'password': password})
        if response.status_code == 200:
            response_data = response.json().get('response')
            userz = User.objects.filter(id=user_id).first()
            userz.muid = response_data.get('muid')
            userz.image = response_data.get('pro_pic')
            userz.save()
            return CustomResponse(general_message="Successfully Muid Connected").get_success_response()
        else:
            return CustomResponse(general_message='Invalid username or password').get_failure_response()


class LoginWithMuid(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        muid = request.data.get('muid').lower()
        password = request.data.get('password')
        URL = DOMAIN_NAME + '/api/v1/auth/iedc-login/'
        response = requests.post(URL, data={'emailOrMuid': muid, 'password': password})

        if response.status_code == 200:
            response_data = response.json().get('response')
            response_data['id'] = uuid.uuid4()
            response_data['image'] = response_data.get('pro_pic')
            user_exists = User.objects.filter(muid=response_data.get('muid')).first()
            if not user_exists:
                serializer = UserRegisterSerializer(data=response_data)
                if serializer.is_valid():
                    user_obj = serializer.save()
                    allocate_group_and_roles(user_obj)
                    user = authenticate(self.request, muid=user_obj.muid)
                    auth = TokenGenerate().generate(user=user)
                    return CustomResponse(response=auth).get_success_response()
                else:
                    return CustomResponse(response=serializer.errors).get_failure_response()
            else:
                user = authenticate(self.request, muid=user_exists.muid)
                auth = TokenGenerate().generate(user=user)
                return CustomResponse(response=auth).get_success_response()
        else:
            return CustomResponse(general_message='Invalid username or password').get_failure_response()


class UserTreasureAPI(APIView):
    authentication_classes = [CustomizePermission]

    def post(self, request):
        treasure_id = request.data.get('id')
        user_id = JWTUtils.fetch_user_id(request)
        treasure = Treasures.objects.filter(id=treasure_id).first()

        if treasure is None:
            return CustomResponse(general_message="Treasure not available").get_failure_response()

        treasure_log = TreasureLog.objects.filter(user_id=user_id, treasure=treasure).first()
        if treasure_log:
            return CustomResponse(general_message='You are already collected this reward').get_success_response()
        if treasure.winner:
            return CustomResponse(
                general_message="Ops! u are unlucky, the treasure is already collected").get_success_response()
        is_winner = False
        if treasure.winner is None:
            treasure.save()
            is_winner = True

        serializer = UserTreasureSerializer(
            data=request.data,
            context={
                'treasure': treasure,
                'user_id': user_id,
                'is_winner': is_winner
            }
        )

        if serializer.is_valid():
            serializer.save()

            return CustomResponse(
                general_message='success'
            ).get_success_response()

        return CustomResponse(
            message=serializer.errors
        ).get_failure_response()


class UserQrCodeAPI(APIView):
    authentication_classes = [CustomizePermission]

    def get(self, request):
        user_id = JWTUtils.fetch_user_id(request)

        user = User.objects.filter(id=user_id).values('id')
        return CustomResponse(response=user).get_success_response()


class UserProfileAPI(APIView):
    authentication_classes = [CustomizePermission]

    def get(self, request):
        user_id = JWTUtils.fetch_user_id(request)

        user = User.objects.filter(id=user_id).first()

        serializer = UserDetailsSerializer(user, many=False).data

        return CustomResponse(
            response=serializer
        ).get_success_response()


class UserQrCodeScanner(APIView):
    authentication_classes = [CustomizePermission]

    def post(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        opponent_user_id = request.data.get('qr_code')

        user_one = User.objects.filter(id=user_id).first()
        user_two = User.objects.filter(id=opponent_user_id).first()
        if not user_two:
            return CustomResponse(general_message="Invalid User").get_failure_response()

        if ScanLog.objects.filter(user1=user_one, user2=user_two).exists():
            return CustomResponse(general_message="Already Connected").get_failure_response()

        ScanLog.objects.create(id=uuid.uuid4(),
                               user1=user_one,
                               user2=user_two,
                               created_at=DateTimeUtils.get_current_utc_time())

        user_one.is_permenent = True
        user_two.is_permenent = True
        user_one.save()
        user_two.save()

        if user_one.group.id == user_two.group.id:
            serializer = UserQrCodeSerializer(user_two, many=False).data
            return CustomResponse(response=serializer).get_success_response()
        return CustomResponse(general_message="Sorry.. He / She is not in your crew..").get_failure_response()


class TreasureShow(APIView):
    authentication_classes = [CustomizePermission]

    def get(self, request):
        user_id = JWTUtils.fetch_user_id(request)

        treasure = Treasures.objects.values(
            'title',
            own=Case(
                When(
                    Q(winner=user_id),
                    then=True),
                default=False,
                output_field=BooleanField()
            ),
            scanned=Case(
                When(
                    Q(treasure_log_treasure__user=user_id),
                    then=True),
                default=False,
                output_field=BooleanField()
            ),
            claimed=Case(
                When(
                    Q(is_claimed=True),
                    then=True),
                default=False,
                output_field=BooleanField()
            )

        )

        return CustomResponse(
            response=treasure
        ).get_success_response()
