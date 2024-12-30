# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RealTimeFormConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Khi client kết nối
        self.room_group_name = 'real_time_form'

        # Tạo một nhóm (group) để các client có thể nhận dữ liệu từ nhau
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Chấp nhận kết nối WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Khi client ngắt kết nối
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Nhận dữ liệu từ WebSocket và phát lại cho tất cả client trong group
    async def receive(self, text_data):
        data = json.loads(text_data)
        cell_data = data['cell_data']

        # Gửi lại dữ liệu cho tất cả các client trong nhóm
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_data',
                'cell_data': cell_data
            }
        )

    # Nhận dữ liệu từ group và gửi lại cho client
    async def send_data(self, event):
        cell_data = event['cell_data']

        # Gửi dữ liệu cho WebSocket của client
        await self.send(text_data=json.dumps({
            'cell_data': cell_data
        }))
