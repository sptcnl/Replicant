from rest_framework import generics
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from .serializers import (
                            SignupSerializer
                        )
from rest_framework.exceptions import ValidationError

from django.contrib.auth import get_user_model

User = get_user_model()

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