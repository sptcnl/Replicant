import re
from rest_framework import generics, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from .serializers import (
                            SignupSerializer
                        )
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from django.contrib.auth import get_user_model

User = get_user_model()

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


@permission_classes([AllowAny])
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def perform_create(self, serializer):
        try:
            # 객체 저장 시도
            serializer.save()
        except Exception as e:
            raise ValidationError({"detail": f"An error occurred: {str(e)}"})


@permission_classes([AllowAny])
class CheckUsernameView(APIView):
    def get(self, request):
        username = request.query_params.get('username', '').strip()
        if not username:
            return Response({'detail': 'username 파라미터가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        exists = User.objects.filter(username=username).exists()
        return Response({'available': not exists})  # true면 사용 가능


@permission_classes([AllowAny])
class CheckEmailView(APIView):
    def get(self, request):
        email = request.query_params.get('email', '').strip()
        if not email:
            return Response({'detail': 'email 파라미터가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        is_email = is_valid_email(email)
        if not is_email:
            return Response({'detail': 'email 형식이 아닙니다.'}, status=status.HTTP_400_BAD_REQUEST)

        exists = User.objects.filter(email=email).exists()
        return Response({'available': not exists})  # true면 사용 가능