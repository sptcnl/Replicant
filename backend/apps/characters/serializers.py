from rest_framework import serializers
from .models import Character, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class CharacterSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = ['name', 'scenario', 'tag']

    def create(self, validated_data):
        # ManyToMany 관계 데이터 분리
        tags_data = validated_data.pop('tag')
        print(tags_data)
        # Character 객체 생성
        character = Character.objects.create(**validated_data)
        # 태그 연결
        if tags_data:
            tag_list = tags_data.split(',')
            tags = []
            for a_tag in tag_list:
                name = a_tag.replace(' ', '')
                tag, created = Tag.objects.get_or_create(name=name)
                tags.append(tag)
            character.tag.set(tags)
        return character