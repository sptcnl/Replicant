from rest_framework import generics, permissions
from .models import Character
from .serializers import CharacterSerializer

class CharacterLCView(generics.ListCreateAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            # List(GET) 요청은 누구나 접근 가능
            return [permissions.AllowAny()]
        elif self.request.method == 'POST':
            # Create(POST) 요청은 관리자만 접근 가능
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)