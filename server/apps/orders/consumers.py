import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'orders_updates'

        #join staff orders group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_layer
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_layer
        )

    async def receive(self, text_data):
        pass

    async def order_update(self, event):
        order = event['order']
        await self.send(text_data=json.dumps({
            'type': 'ORDER_UPDATE',
            'order': order
        }))