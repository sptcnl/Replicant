from django.urls import path
from . import views

urlpatterns = [
    path("room/", views.RoomLView.as_view()),
    path("<str:room_id>/", views.ChatLView.as_view()),
]