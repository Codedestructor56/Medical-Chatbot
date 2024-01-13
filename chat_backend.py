from flask import Flask, request, abort, jsonify
from flask_socketio import SocketIO
from user_auth import User
from database import Database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

class Chatbot:
    def __init__(self):
        self.users = {}

    def process_query(self,db, user_input, user_id, chat_id):
        user_data = db.get_user_data(user_id)
        if user_data:
            abort(404, f"User with ID {user_id} does not exist")

        user = self.users[user_id]

        if chat_id not in user.chats:
            abort(404, f"Chat with ID {chat_id} does not exist for User {user_id}")

        try:
            response = user.chats[chat_id].conversation_chat(user_input)
            return {
                'chat_id': chat_id,
                'bot_response': response
            }
        except AttributeError as e:
            return {"error": "You haven't initialized the conversation yet; use the /create_new_chat endpoint to do that first"}

    def create_user(self, email, password):
        user = User(email, password)
        user_id = user.user_id
        self.users[user_id] = user
        return {'status': f'User created.','id':f"{user_id}"}

    def delete_chat(self, user_id, chat_id):
        if user_id not in self.users:
            return {'error': f'User with ID {user_id} does not exist.'}

        user = self.users[user_id]
        if chat_id not in user.chats:
            return {'error': f'Chat with ID {chat_id} does not exist for User {user_id}.'}

        user.delete_chat(chat_id)
        return {'status': f'Chat with ID {chat_id} deleted for User {user_id}.'}

    def delete_user(self, user_id):
        if user_id not in self.users:
            return {'error': f'User with ID {user_id} does not exist.'}
        
        del self.users[user_id]
        return {'status': f'User with ID {user_id} deleted.'}

    def get_users(self):
        return list(self.users.keys())

chatbot = Chatbot()
database = Database()

@app.route('/create_new_user', methods=['POST'])
def create_new_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required."})

    response_data = chatbot.create_user(email, password)
    if 'status' in response_data:
        user = chatbot.users[response_data['id']]
        user.add_to_database(database)
    return jsonify(response_data)

@app.route("/delete_user/<string:user_id>", methods=['POST'])
def delete_user(user_id):
    user = database.get_user_data(user_id)
    if user:
        database.delete_user_data(user_id)
        chatbot.delete_user(user_id)
        return {'status': f'User with ID {user_id} deleted.'}
    else:
        return {'error': f'User with ID {user_id} does not exist.'}

@app.route('/create_new_chat/<string:user_id>', methods=['POST'])
def create_new_chat(user_id):
    user = chatbot.users.get(user_id)
    response_data = user.create_chat(user_id)
    if 'status' in response_data:
        user = chatbot.users[user_id]
        chat_id = response_data['chat_id']
        chat_history = user.chats[chat_id].history
        user.add_chat_to_database(chat_id, chat_history)
    return jsonify(response_data)

@app.route("/delete_chat/<string:user_id>/<string:chat_id>", methods=["POST"])
def delete_chat(user_id, chat_id):
    user = chatbot.users.get(user_id)
    if user and chat_id in user.chats:
        user.delete_chat(chat_id)
        user.database.update_user_data(user_id, {"$pull": {"chats": {"chat_id": chat_id}}})
        return {'status': f'Chat with ID {chat_id} deleted for User {user_id}.'}
    else:
        return {'error': f'Chat with ID {chat_id} does not exist for User {user_id}.'}


@app.route('/get_message', methods=['POST'])
def get_message():
    data = request.get_json()
    query = data.get("message")
    user_id = data.get("user_id")
    chat_id = data.get("chat_id")
    response_data = chatbot.process_query(user_input=query, user_id=user_id, chat_id=chat_id)
    return jsonify(response_data)

@app.route("/get_chat_ids/<string:user_id>", methods=['GET'])
def get_chats(user_id):
    if user_id not in chatbot.users:
        return {'error': f'User with ID {user_id} does not exist'}

    user = chatbot.users[user_id]
    user_chats = user.get_user_chats()
    return jsonify(user_chats)

@app.route("/get_user_ids",methods=['POST'])
def get_users():
    return jsonify(chatbot.get_users())

if __name__ == "__main__":
    socketio.run(app, debug=True)


