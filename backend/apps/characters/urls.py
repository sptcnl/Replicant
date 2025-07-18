from django.urls import path
from . import views

urlpatterns = [
    path("", views.CharacterLCView.as_view()),
    path("<str:pk>/", views.CharacterRUDView.as_view()),
    path("tag/list/", views.tag_list),
]