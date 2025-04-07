import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, ConversationMessage
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            # Log the authentication failure
            print(f"WebSocket connection rejected: User is anonymous")
            await self.close(code=4001)  # Unauthorized
            return

        # Add to user's personal channel
        self.user_channel = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.user_channel,
            self.channel_name
        )

        print(
            f"WebSocket connected: User {self.user.username} (ID: {self.user.id})")
        await self.accept()

    async def disconnect(self, close_code):
        # Remove from user's personal channel
        if hasattr(self, 'user_channel'):
            await self.channel_layer.group_discard(
                self.user_channel,
                self.channel_name
            )
        print(f"WebSocket disconnected: code {close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'send_message':
                chat_id = data.get('chat_id')
                message_content = data.get('message')

                # Save message to database
                message = await self.save_message(chat_id, message_content)

                # Get participants to notify
                participants = await self.get_chat_participants(chat_id)

                # Notify all participants
                for participant in participants:
                    await self.channel_layer.group_send(
                        f"user_{participant.id}",
                        {
                            'type': 'chat_message',
                            'message': {
                                'id': message.id,
                                'content': message.content,
                                'sent_by': message.sent_by.id,
                                'sent_by_username': message.sent_by.username,
                                'date_created': message.date_created.isoformat(),
                                'is_read': False
                            },
                            'chat_id': chat_id
                        }
                    )

            elif message_type == 'mark_read':
                message_id = data.get('message_id')
                chat_id = data.get('chat_id')

                # Mark message as read in database
                await self.mark_message_read(message_id)

                # Notify other participants
                participants = await self.get_chat_participants(chat_id)
                for participant in participants:
                    if participant.id != self.user.id:
                        await self.channel_layer.group_send(
                            f"user_{participant.id}",
                            {
                                'type': 'message_read',
                                'message_id': message_id,
                                'chat_id': chat_id
                            }
                        )
        except Exception as e:
            print(f"Error in WebSocket receive: {str(e)}")

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'chat_id': event['chat_id']
        }))

    async def message_read(self, event):
        # Send message read notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id'],
            'chat_id': event['chat_id']
        }))

    @database_sync_to_async
    def save_message(self, chat_id, content):
        try:
            conversation = Conversation.objects.get(id=chat_id)
            message = ConversationMessage.objects.create(
                conversation=conversation,
                sent_by=self.user,
                content=content
            )
            return message
        except Conversation.DoesNotExist:
            raise ValueError("Conversation not found")

    @database_sync_to_async
    def get_chat_participants(self, chat_id):
        conversation = Conversation.objects.get(id=chat_id)
        return list(conversation.participants.all())

    @database_sync_to_async
    def mark_message_read(self, message_id):
        message = ConversationMessage.objects.get(id=message_id)
        message.is_read = True
        message.save()
        return message
