from bcrypt import hashpw, gensalt
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status

from accounts import models
from accounts.serializers import AccessTokensSerializer, RefreshTokensSerializer


class AUTH:
    @staticmethod
    def generate_tokens(user_id, request):
        try:
            data = {
                "access_token": {
                    'token': (hashpw(str('accessToken').encode('UTF_8') + str(datetime.now()).encode('UTF_8') + str(user_id).encode('UTF_8'), gensalt())).decode('ascii'),
                    'created_at': datetime.today(),
                    'expired_at': datetime.today() + timedelta(minutes=720)
                },
                'refresh_token': {
                    'token': (hashpw(str('refreshToken').encode('UTF_8') + str(datetime.now()).encode('UTF_8') + str(user_id).encode('UTF_8'), gensalt())).decode('ascii'),
                    'created_at': datetime.today(),
                    'expired_at': datetime.today() + timedelta(minutes=4320)
                }

            }

            if request.META.get('HTTP_AUTHORIZATION'):
                # print(request.META.get('HTTP_AUTHORIZATION').split(' '))
                # prev_token = models.AccessTokens.objects.filter(user_id=user_id)
                # print('prev token', prev_token)
                # # if prev_token:
                # #     models.AccessTokens.objects.get(id=prev_token.access_token_id.id).delete()

                access_data = {
                    'access_token': data['access_token']['token'],
                    'user_id': user_id,
                    'expired_at': data['access_token']['expired_at'],
                    'created_at': data['access_token']['created_at'],
                }
                access_serializer = AccessTokensSerializer(data=access_data)
                if access_serializer.is_valid():
                    access_serializer.save()

                if access_serializer.data:
                    refresh_data = {
                        'access_token_id': access_serializer.data['id'],
                        'refresh_token': data['refresh_token']['token'],
                        'user_id': user_id,
                        'expired_at': data['refresh_token']['expired_at'],
                        'created_at': data['refresh_token']['created_at']
                    }
                    refresh_serializer = RefreshTokensSerializer(data=refresh_data)
                    if refresh_serializer.is_valid():
                        refresh_serializer.save()
                    return data
                else:
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as err:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def sign_out(request):
        try:
            print(request.META.get('HTTP_AUTHORIZATION'))
            token = request.META.get('HTTP_AUTHORIZATION')
            find_token = models.AccessTokens.objects.filter(access_token=token)
            if find_token:
                find_token.delete()

        except Exception as err:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
