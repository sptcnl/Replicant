import json, os, environ, uuid, logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Chat
from apps.characters.models import Character, Tag, CharacterTag
from .llm import graph, save_metadata, load_metadata, save_chat, load_chat
from config.settings import BASE_DIR

env = environ.Env(DEBUG=(bool, True))

environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

gemini_api_key = env("GEMINI_API_KEY")

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.character_id = self.scope['url_route']['kwargs']['room_id']
        self.user = self.scope["user"]
        logging.info(f"self.user: {self.user}")
        logging.info(f"self.users type: {type(self.user)}")

        # 방 존재 및 권한 체크
        room = await self.get_or_create_room(self.character_id, self.user)
        logging.info({
            "id": str(room.id),
            "user_id": room.user_id,
            "character_id": str(room.character_id),
            "created_at": room.created_at.isoformat(),
        })

        if not room or room.user_id != self.user.id:
            logging.info('방 없음 또는 방의 주인이 아님')
            await self.close()
            return

        self.room_id = room.id
        self.room_group_name = f'chat_{self.room_id}'

        # 그룹에 참여 (여러 클라이언트 동시 접속 가능)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 그룹에서 나가기
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        logging.info(f"receive data: {data}")
        content = data.get('content')
        sender_type = data.get('sender_type')
        action = data.get('action')

        # action(재생성, 유저 답변 건너뛰기)에 따라 변경
        if action == 'regenerate_response':
            await self.handle_regenerate_response(data)
            return
        elif action == 'ai_only_response':
            await self.handle_ai_only_response(data)
            return

        logging.info(f"sender_type: {sender_type}")

        # 유저 메시지 저장
        chat = await self.save_chat(
            room_id=self.room_id,
            content=content,
            sender_type=sender_type
        )

        # AI 답변 생성
        if sender_type == 'U':  # 유저가 보낸 경우에만 AI 답변
            ai_response = await self.get_ai_response(content)
            ai_chat = await self.save_chat(
                room_id=self.room_id,
                content=ai_response,
                sender_type='A'  # AI
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': str(ai_chat.id),
                        'content': ai_response,
                        'sender_type': 'A',
                        'created_at': ai_chat.created_at.isoformat(),
                    }
                }
            )

    async def handle_ai_only_response(self, data):
        """유저 답변 건너뛰고 AI 응답만 생성"""
        room_id = data['room_id']

        # 가장 최근 유저 메시지 가져오기
        user_message = await self.get_last_user_message(room_id)
        if not user_message:
            return
        
        # 이전 AI 답변 삭제
        await self.delete_last_ai_response(room_id)
        
        # AI 답변 생성 (유저 메시지는 저장하지 않음)
        ai_response = await self.generate_ai_response(user_message)
        
        # AI 답변 저장 및 전송
        ai_chat = await self.save_chat(
            room_id=room_id,
            content=ai_response,
            sender_type='A'  # AI
        )
        
        # 그룹에 AI 메시지 전송
        await self.channel_layer.group_send(
            f"chat_{room_id}",
            {
                'type': 'chat_message',
                'message': {
                    'id': str(ai_chat.id),
                    'content': ai_response,
                    'sender_type': 'A',
                    'created_at': ai_chat.created_at.isoformat()
                }
            }
        )

    async def handle_regenerate_response(self, data):
        """AI 답변 재생성"""
        room_id = data['room_id']
        user_message = data['last_user_message']
        
        # 기존 AI 답변 삭제
        await self.delete_last_ai_response(room_id)
        
        # 새 답변 생성
        new_response = await self.generate_ai_response(user_message)
        
        # 새 답변 저장 및 전송
        new_chat = await self.save_chat(
            room_id=room_id,
            content=new_response,
            sender_type='A'
        )
        await self.channel_layer.group_send(
            f"chat_{room_id}",
            {
                'type': 'chat_message',
                'message': {
                    'id': str(new_chat.id),
                    'content': new_response,
                    'sender_type': 'A'
                }
            }
        )

    @database_sync_to_async
    def delete_last_ai_response(self, room_id):
        """마지막 AI 답변 삭제"""
        Chat.objects.filter(
            room__id=room_id, 
            sender_type='A'
        ).last().delete()


    @database_sync_to_async
    def get_ai_response(self, user_message):
        current_state = {
            "input_text": "", 
            "output_text": "", 
            "history": []
        }

        config = {
            "configurable": {
                "llm": {"type": "gemini", "api_key": gemini_api_key},
                "thread_id": self.room_id,
                "session_id": self.room_id,
                "user_id": self.user.id,
            }
        }

        logging.info(f"get_ai_response/config: {config}")

        current_state["input_text"] = user_message
        result = graph.invoke(current_state, config=config)
        current_state = {
            "input_text": "",
            "output_text": "",
            "history": result["history"]
        }
        return result["output_text"]

    @database_sync_to_async
    def get_last_user_message(self, room_id):
        # 가장 최근 유저 메시지 가져오기
        return Chat.objects.filter(
            room__id=room_id,
            sender_type='U'
        ).last().content if Chat.objects.filter(
            room__id=room_id,
            sender_type='U'
        ).exists() else None

    async def chat_message(self, event):
        # 메시지 수신 처리
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    @database_sync_to_async
    def get_or_create_room(self, character_id, user):
        combined_str = character_id + str(user.id)
        room_id = uuid.uuid5(uuid.NAMESPACE_DNS, combined_str)
        try:
            room, created = Room.objects.get_or_create(id=room_id, user=user, character_id=character_id)
            logging.info(f"room_obj: {room.__dict__}")
            if created:
                character_obj = Character.objects.get(id=character_id)
                tag_names = list(
                    character_obj.tag.values_list("name", flat=True)
                )
                logging.info(f"character_obj: {character_obj.__dict__}")
                logging.info(f"tag_names: {tag_names}")
                character_data = {
                    "name": character_obj.name,
                    "personality": tag_names,
                    "scenario": character_obj.scenario
                }
                is_saved = save_metadata(str(room.id), character_data)
                if is_saved:
                    metadata = load_metadata(str(room.id))
                    logging.info(f"character_metadata_save_check: {metadata}")
            return room
        except Exception as e:
            logging.error(e)
            return None

    @database_sync_to_async
    def get_chats(self, room_id):
        chats = Chat.objects.filter(room__id=room_id).order_by('created_at')
        logging.info(f"get_chats: {chats}")
        logging.info(f"get_chats_to_chat: {[
            {
                'id': str(chat.id),
                'content': chat.content,
                'sender_type': chat.sender_type,
                'created_at': chat.created_at.isoformat(),
            }
            for chat in chats
        ]}")
        return [
            {
                'id': str(chat.id),
                'content': chat.content,
                'sender_type': chat.sender_type,
                'created_at': chat.created_at.isoformat(),
            }
            for chat in chats
        ]

    @database_sync_to_async
    def save_chat(self, room_id, content, sender_type):
        room = Room.objects.get(id=room_id)
        chat = Chat.objects.create(
            room=room,
            content=content,
            sender_type=sender_type
        )
        return chat