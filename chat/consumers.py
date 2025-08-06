import json
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import redis.asyncio as redis
from django.conf import settings

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = None
        self.user_id = None
        self.room_name = None
        self.partner_channel = None
        self.is_matched = False
        self.connection_time = None
        
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Initialize Redis connection
            redis_url = settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Generate unique user ID
            self.user_id = str(uuid.uuid4())
            self.connection_time = datetime.now()
            
            # Accept the WebSocket connection
            await self.accept()
            
            # Log connection
            logger.info(f"User {self.user_id} connected from {self.scope['client']}")
            
            # Send waiting status
            await self.send(text_data=json.dumps({
                'type': 'status',
                'message': 'Looking for someone to chat with...',
                'status': 'waiting'
            }))
            
            # Try to find a match
            await self.find_match()
            
        except Exception as e:
            logger.error(f"Error in connect: {e}")
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            if self.is_matched and self.partner_channel:
                # Notify partner about disconnection
                await self.channel_layer.send(self.partner_channel, {
                    'type': 'partner_disconnected'
                })
            
            # Remove from waiting queue
            if self.redis_client:
                await self.redis_client.lrem('waiting_users', 0, self.user_id)
                await self.redis_client.delete(f'user:{self.user_id}:channel')
                
            # Leave room if in one
            if self.room_name:
                await self.channel_layer.group_discard(self.room_name, self.channel_name)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
                
            # Log disconnection
            duration = datetime.now() - self.connection_time if self.connection_time else None
            logger.info(f"User {self.user_id} disconnected. Duration: {duration}")
            
        except Exception as e:
            logger.error(f"Error in disconnect: {e}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                message = data.get('message', '').strip()
                if message and self.is_matched and self.partner_channel:
                    # Sanitize message
                    message = self.sanitize_message(message)
                    
                    # Send to partner
                    await self.channel_layer.send(self.partner_channel, {
                        'type': 'chat_message',
                        'message': message,
                        'sender': 'stranger'
                    })
                    
                    # Send confirmation to sender
                    await self.send(text_data=json.dumps({
                        'type': 'message',
                        'message': message,
                        'sender': 'you',
                        'timestamp': datetime.now().isoformat()
                    }))
                    
            elif message_type == 'next':
                await self.find_new_partner()
                
            elif message_type == 'typing':
                if self.is_matched and self.partner_channel:
                    await self.channel_layer.send(self.partner_channel, {
                        'type': 'typing_indicator',
                        'typing': data.get('typing', False)
                    })
                    
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from user {self.user_id}")
        except Exception as e:
            logger.error(f"Error in receive: {e}")

    async def find_match(self):
        """Find a partner for the user"""
        try:
            # Store user's channel name in Redis
            await self.redis_client.set(
                f'user:{self.user_id}:channel', 
                self.channel_name, 
                ex=3600  # Expire in 1 hour
            )
            
            # Try to get a waiting user
            waiting_user = await self.redis_client.lpop('waiting_users')
            
            if waiting_user and waiting_user != self.user_id:
                # Found a match
                partner_channel = await self.redis_client.get(f'user:{waiting_user}:channel')
                
                if partner_channel:
                    await self.create_chat_room(waiting_user, partner_channel)
                else:
                    # Partner channel not found, add self to queue
                    await self.redis_client.rpush('waiting_users', self.user_id)
            else:
                # No one waiting, add self to queue
                if waiting_user == self.user_id:
                    # Put it back if it was our own ID
                    await self.redis_client.rpush('waiting_users', waiting_user)
                await self.redis_client.rpush('waiting_users', self.user_id)
                
        except Exception as e:
            logger.error(f"Error in find_match: {e}")

    async def create_chat_room(self, partner_id, partner_channel):
        """Create a chat room with a partner"""
        try:
            # Generate room name
            self.room_name = f'chat_{uuid.uuid4()}'
            self.partner_channel = partner_channel
            self.is_matched = True
            
            # Add both users to the room
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.channel_layer.group_add(self.room_name, partner_channel)
            
            # Notify both users
            await self.channel_layer.group_send(self.room_name, {
                'type': 'match_found'
            })
            
            # Update partner's state
            await self.channel_layer.send(partner_channel, {
                'type': 'set_partner',
                'partner_channel': self.channel_name,
                'room_name': self.room_name
            })
            
            logger.info(f"Created room {self.room_name} for users {self.user_id} and {partner_id}")
            
        except Exception as e:
            logger.error(f"Error creating chat room: {e}")

    async def find_new_partner(self):
        """Leave current chat and find a new partner"""
        try:
            if self.is_matched and self.partner_channel:
                # Notify current partner
                await self.channel_layer.send(self.partner_channel, {
                    'type': 'partner_left'
                })
                
            # Leave current room
            if self.room_name:
                await self.channel_layer.group_discard(self.room_name, self.channel_name)
                
            # Reset state
            self.room_name = None
            self.partner_channel = None
            self.is_matched = False
            
            # Send waiting status
            await self.send(text_data=json.dumps({
                'type': 'status',
                'message': 'Looking for someone new to chat with...',
                'status': 'waiting'
            }))
            
            # Find new match
            await self.find_match()
            
        except Exception as e:
            logger.error(f"Error finding new partner: {e}")

    def sanitize_message(self, message):
        """Sanitize user message"""
        # Remove excessive whitespace
        message = ' '.join(message.split())
        
        # Limit length
        if len(message) > 500:
            message = message[:500]
            
        return message

    # Channel layer event handlers
    async def chat_message(self, event):
        """Handle chat message from partner"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': datetime.now().isoformat()
        }))

    async def match_found(self, event):
        """Handle match found event"""
        await self.send(text_data=json.dumps({
            'type': 'status',
            'message': 'Connected to a stranger! Say hello.',
            'status': 'connected'
        }))

    async def partner_disconnected(self, event):
        """Handle partner disconnection"""
        self.is_matched = False
        self.partner_channel = None
        
        await self.send(text_data=json.dumps({
            'type': 'status',
            'message': 'Stranger has disconnected. Looking for someone new...',
            'status': 'waiting'
        }))
        
        # Find new match
        await self.find_match()

    async def partner_left(self, event):
        """Handle partner leaving for new chat"""
        self.is_matched = False
        self.partner_channel = None
        
        await self.send(text_data=json.dumps({
            'type': 'status',
            'message': 'Stranger has found someone new. Looking for another person...',
            'status': 'waiting'
        }))
        
        # Find new match
        await self.find_match()

    async def set_partner(self, event):
        """Set partner information"""
        self.partner_channel = event['partner_channel']
        self.room_name = event['room_name']
        self.is_matched = True

    async def typing_indicator(self, event):
        """Handle typing indicator"""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'typing': event['typing']
        }))