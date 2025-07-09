from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Character, Tag
from .serializers import CharacterSerializer, TagNameListSerializer

class CharacterLCView(generics.ListCreateAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            # List(GET) 요청은 누구나 접근 가능
            return [permissions.AllowAny()]
        elif self.request.method == 'POST':
            # Create(POST) 요청은 로그인 한 회원만 접근 가능
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tag_list(request):
    tag_names = Tag.objects.values_list('name', flat=True)
    serializer = TagNameListSerializer(tag_names)
    return Response(serializer.data)