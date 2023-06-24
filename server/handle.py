import sys
import threading
import db

mutex = threading.Lock()

websocket_online = {}
group_websockets = {}

async def send(websocket, message):
    print(f'send to {websocket.remote_address}: {message}', file=sys.stderr)
    await websocket.send(message)

async def handle_login(lines, websocket):
    if len(lines) != 2:
        await send(websocket, 'UNEXPECTED FORMAT')
        return
    username, password = lines
    table = db.check_password(username, password)
    assert(len(table) <= 1)
    if len(table) == 0:
        await send(websocket, 'WRONG')
        return
    id = table[0][0]
    await send(websocket, f'OK\n{id}')

async def handle_sign_up(lines, websocket):
    if len(lines) != 2:
        await send(websocket, 'UNEXPECTED FORMAT')
        return
    username, password = lines
    table = db.check_username(username)
    if len(table) != 0:
        # 存在对应的user，注册失败
        await send(websocket, 'EXIST')
    else:
        db.new_user(username, password)
        await send(websocket, 'OK') 

async def get_username(lines, websocket):
    if len(lines) != 1:
        await send(websocket, 'UNEXPECTED FORMAT')
        return
    id = int(lines[0])
    name = db.get_username(id)
    if name == None:
        await send(websocket, 'UNEXPECTED DATA')
    else:
        await send(websocket, f'{name}')

async def get_group_list(lines, websocket):
    if len(lines) != 1:
        await send(websocket, 'UNEXPECTED FORMAT')
        return
    id = lines[0]
    table = db.get_group_ids(id)
    ret = ''
    for row in table:
        group_id = row[0]
        ret += f'{group_id}\n'
    await send(websocket, ret)

async def get_friend_list(lines, websocket):
    if len(lines) != 1:
        await send(websocket, 'UNEXPECTED FORMAT')
        return
    id = lines[0]
    table = db.get_friend_list(id)
    ret = ''
    for row in table:
        frined_id = row[1] if row[0] == int(id) else row[0]
        name = db.get_username(frined_id)
        ret += f'{frined_id}\n{name}\n'
    await send(websocket, ret)

async def start(lines, websocket):
    assert(len(lines) == 1)
    id = int(lines[0])
    username = db.get_username(id)
    log = db.get_DM_messages(id)
    for i in log:
        if int(i[0]) == id:
            tid = db.get_target_id(i[2], i[0])
            await send(websocket, f'DM\n{tid}\n{username}\n{i[1]}')
        else:
            name = db.get_username(i[0])
            await send(websocket, f'DM\n{i[0]}\n{name}\n{i[1]}')
    websocket_online[id] = websocket
    table = db.get_group_ids(id)
    for row in table:
        group_id = row[0]
        log = db.get_group_message(group_id)
        for i in log:
            await send(websocket, f'group message\n{i[0]}\n{i[1]}\n{i[2]}')
        if not group_id in group_websockets:
            group_websockets[group_id] = set()
        group_websockets[group_id].add(websocket)


async def add_friend(lines, websocket):
    assert(len(lines) == 2)
    id1 = int(lines[0])
    id2 = int(lines[1])
    table = db.get_username(id2)
    if table == None:
        return
    if id1 > id2:
        id1, id2 = id2, id1
    if id1 == id2:
        return
    table = db.get_DM_id(id1, id2)
    if len(table) != 0:
        return
    db.new_DM(id1, id2)
    if id1 in websocket_online:
        name = db.get_username(id2)
        await send(websocket_online[id1], f'add friend\n{id2}\n{name}')
    if id2 in websocket_online:
        name = db.get_username(id1)
        await send(websocket_online[id2], f'add friend\n{id1}\n{name}')

async def add_group(lines, websocket):
    assert(len(lines) == 2)
    user_id = int(lines[0])
    group_id = int(lines[1])
    table = db.check_user_in_group(user_id, group_id)
    if len(table) != 0:
        return
    db.add_group(user_id, group_id)
    if not group_id in group_websockets:
        group_websockets[group_id] = set()
    group_websockets[group_id].add(websocket)

async def send_dm(lines, websocket):
    user_id = int(lines[0])
    target_id = int(lines[1])
    message = '\n'.join(lines[2:])
    id1 = int(lines[0])
    id2 = int(lines[1])
    if id1 > id2:
        id1, id2 = id2, id1
    table = db.get_DM_id(id1, id2)
    if len(table) == 0:
        return
    chat_id = table[0][0]
    db.add_DM_message(chat_id, user_id, message)
    if target_id in websocket_online:
        try:
            username = db.get_username(user_id)
            await send(websocket_online[target_id], f'DM\n{user_id}\n{username}\n{message}')
        except:
            pass

async def send_group(lines, websocket):
    user_id = int(lines[0])
    username = db.get_username(user_id)
    group_id = int(lines[1])
    message = '\n'.join(lines[2:])
    db.add_group_message(group_id, user_id, message)
    for i in group_websockets[group_id]:
        try:
            await send(i, f'group message\n{group_id}\n{username}\n{message}')
        except:
            pass