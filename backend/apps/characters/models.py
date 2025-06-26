import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Character(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="own_character"
    )
    tag = models.ManyToManyField(
        Tag, through="CharacterTag", related_name="tag_character", 
    )
    name = models.CharField(max_length=10)
    scenario = models.TextField(default="")

    def __str__(self):
        return self.name


class CharacterTag(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)