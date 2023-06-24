import asyncio
from time import sleep
import websockets
import db
import handle
import sys

# 连接到MySQL数据库

db.init()

async def handle_connection(websocket, path):
    print(f"Client connected: {websocket.remote_address}")
    try:
        while True:
            message = await websocket.recv()
            print(f'recieved from {websocket.remote_address}: {message}', file=sys.stderr)
            # 使用 splitlines() 方法拆分为行列表
            lines = message.splitlines()
            if lines[0] == 'LOGIN':
                await handle.handle_login(lines[1:], websocket)
            elif lines[0] == 'SIGN UP':
                await handle.handle_sign_up(lines[1:], websocket)
            elif lines[0] == 'get group list':
                await handle.get_group_list(lines[1:], websocket)
            elif lines[0] == 'get friend list':
                await handle.get_friend_list(lines[1:], websocket)
            elif lines[0] == 'get username':
                await handle.get_username(lines[1:], websocket)
            elif lines[0] == 'START':
                await handle.start(lines[1:], websocket)
            elif lines[0] == 'add friend':
                await handle.add_friend(lines[1:], websocket)
            elif lines[0] == 'add group':
                await handle.add_group(lines[1:], websocket)
            elif lines[0] == 'send DM':
                await handle.send_dm(lines[1:], websocket)
            elif lines[0] == 'send group':
                await handle.send_group(lines[1:], websocket)

    except  (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
        # handle.close(websocket)
        print(f"Client disconnected: {websocket.remote_address}")


# 启动 WebSocket 服务器
start_server = websockets.serve(handle_connection, 'localhost', 8765, open_timeout=None)

# 运行事件循环
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

# 关闭数据库连接

# cnx.close()