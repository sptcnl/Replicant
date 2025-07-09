from rest_framework import serializers
from .models import Character, Tag


class CharacterSerializer(serializers.ModelSerializer):
    read_tag = serializers.SlugRelatedField(
        many = True,
        read_only = True,
        slug_field = 'name'
    )
    write_tag = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )

    class Meta:
        model = Character
        fields = ['id', 'profile_img', 'name', 'scenario', 'read_tag', 'write_tag']

    def create(self, validated_data):
        # ManyToMany 관계 데이터 분리
        tags_data = validated_data.pop('write_tag', [])
        print(tags_data)
        # Character 객체 생성
        character = Character.objects.create(**validated_data)
        # 태그 연결
        if tags_data:
            tags = []
            for tag_name in tags_data:
                name = tag_name.replace(' ', '')
                tag, _ = Tag.objects.get_or_create(name=name)
                tags.append(tag)
            character.tag.set(tags)
        return character