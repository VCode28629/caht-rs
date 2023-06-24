import mysql.connector 

cnx = None

def init():
    global cnx
    cnx = mysql.connector.connect(
        host='localhost',
        user='caht',
        password='114514'
    )
    cursor = cnx.cursor()
    database = 'caht'
    cursor.execute("CREATE DATABASE IF NOT EXISTS %s" % (database,   ))

    # 连接到数据库caht
    cnx.database = database

    # 创建表User（如果不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)

    # 创建表PrivateChats（如果不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PrivateChats (
            chat_id INT PRIMARY KEY AUTO_INCREMENT,
            chater_id1 INT NOT NULL,
            chater_id2 INT NOT NULL,
            FOREIGN KEY (chater_id1) REFERENCES User(user_id),
            FOREIGN KEY (chater_id2) REFERENCES User(user_id),
            UNIQUE (chater_id1, chater_id2),
            CHECK(chater_id1 < chater_id2)
        )
    """)

    # 创建表PrivateChatMessages（如果不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PrivateChatMessages (
            Primessage_id INT PRIMARY KEY AUTO_INCREMENT,
            Prichat_id INT NOT NULL,
            DateStamp DATETIME NOT NULL default CURRENT_TIMESTAMP,
            sender INT NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY (Prichat_id) REFERENCES PrivateChats(chat_id),
            FOREIGN KEY (sender) REFERENCES User(user_id)
        )
    """)

    # 创建表GroupChatMembers（如果不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS GroupChatMembers (
            group_id INT,
            user_id INT,
            PRIMARY KEY (group_id, user_id),
            FOREIGN KEY (user_id) REFERENCES User(user_id)
        )
    """)

    # 创建表GroupChatMessages（如果不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS GroupChatMessages (
            Gromessage_id INT PRIMARY KEY AUTO_INCREMENT,
            group_id INT,
            DateStamp DATETIME not null default CURRENT_TIMESTAMP,
            sender INT,
            message TEXT NOT NULL,
            FOREIGN KEY (group_id) REFERENCES GroupChatMembers(group_id),
            FOREIGN KEY (sender) REFERENCES User(user_id)
        );
    """)
    cursor.close()

def select(sql, args=tuple()):
    cursor = cnx.cursor()
    cursor.execute(sql, args)
    result = cursor.fetchall()
    cursor.close()
    return result

def insert(sql, args=tuple()):
    cursor = cnx.cursor()
    cursor.execute(sql, args)
    cnx.commit()
    cursor.close()

def get_DM_messages(id):
    return select('select sender, message, Prichat_id from privatechatmessages t1 join privatechats t2 on t1.prichat_id = t2.chat_id where t2.chater_id1 = %s or t2.chater_id2 = %s order by datestamp asc', (id, id))

def get_username(id):
    table = select('select username from user where user_id = %s', (id, ))
    if len(table) > 0:
        return table[0][0]
    return None

def get_friend_list(id):
    return select('select chater_id1, chater_id2 from privatechats where chater_id1 = %s or chater_id2 = %s', (id, id))

def get_target_id(cid, uid):
    table = select('select chater_id1, chater_id2 from privatechats where chat_id = %s', (cid,))
    if table[0][0] == uid:
        return int(table[0][1])
    return int(table[0][2])

def get_group_ids(id):
    return select('select group_id from groupchatmembers where user_id = %s', (id, ))

def get_group_message(group_id):
    return select('select group_id, username, message from groupchatmessages join user on sender = user_id where group_id = %s order by datestamp asc limit 30', (group_id,))

def check_password(username, password):
    return select('select user_id from user where username = %s and password = %s', (username, password))

def check_username(username):
    return select('select user_id, password from user where username = %s', (username, ))

def get_DM_id(id1, id2):
    return select('select chat_id from privatechats where chater_id1 = %s and chater_id2 = %s', (id1, id2))

def check_user_in_group(user_id, group_id):
    return select('select * from groupchatmembers where user_id = %s and group_id = %s', (user_id, group_id))

def new_user(username, password):
    insert('insert into user (username, password) values (%s, %s)', (username, password))

def new_DM(id1, id2):
    insert('insert into privatechats (chater_id1, chater_id2) values (%s, %s)', (id1, id2))

def add_group(user_id, group_id):
    insert('insert into groupchatmembers (user_id, group_id) values (%s, %s)', (user_id, group_id))

def add_DM_message(chat_id, user_id, message):
    insert('insert into privatechatmessages (prichat_id, sender, message) values (%s, %s, %s)', (chat_id, user_id, message))

def add_group_message(group_id, user_id, message):
    insert('insert into groupchatmessages (group_id, sender, message) values (%s, %s, %s)', (group_id, user_id, message))
