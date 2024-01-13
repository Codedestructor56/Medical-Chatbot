from chatbot import Chat
import uuid

class User:
    MAX_CHATS_PER_USER = 5

    def __init__(self, username, password):
        self.user_id = str(uuid.uuid4())
        self.username = username
        self.password = password
        self.chats = {}

    def create_chat(self, file_path='data/medquad.txt'):
        if len(self.chats) >= self.MAX_CHATS_PER_USER:
            return {'error': f'User {self.user_id} has reached the maximum number of chats.'}

        chat = Chat()
        chat.create_chat(file_path=file_path)
        self.chats[chat.chat_id] = chat
        return {'status': f'New chat created for User {self.user_id}. Chat ID: {chat.chat_id}'}

    def delete_chat(self, chat_id):
        if chat_id in self.chats:
            del self.chats[chat_id]
            return {'status': f'Chat with ID {chat_id} deleted for User {self.user_id}'}
        else:
            return {'error': f'Chat with ID {chat_id} does not exist for User {self.user_id}'}

    def get_user_chats(self):
        chat_data = {}
        for chat_id, chat_instance in self.chats.items():
            chat_data[chat_id] = {
                'chat_id': chat_id,
                'history': chat_instance.history,
                'message_count': chat_instance.message_count
            }
        return chat_data

    def to_dict(self):
        return {
            "_id": self.user_id,
            "username": self.username,
            "password": self.password,
            "chats": [
                {
                    "chat_id": chat_id,
                    "chat_history": chat_instance.history,
                    "message_count": chat_instance.message_count
                }
                for chat_id, chat_instance in self.chats.items()
            ]
        }

    def add_to_database(self, database):
        user_data = self.to_dict()
        database.insert_user_data(user_data)
        return {'status': f'User {self.user_id} added to the database.'}

