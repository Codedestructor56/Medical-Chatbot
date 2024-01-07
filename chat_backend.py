from flask import Flask, request, abort, jsonify
from flask_socketio import SocketIO, emit
from chatbot import Chat

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

class Chatbot:
    def __init__(self):
        self.chats = {} 

    def process_query(self, user_input, chat_id):
        if chat_id not in self.chats:
            abort(404, f"Chat with ID {chat_id} does not exist")

        try:
            response = self.chats[chat_id].conversation_chat(user_input)
            return {
                'chat_id': chat_id,
                'bot_response': response
            }
        except AttributeError as e:
            return {"error": "You haven't initialized the conversation yet, use the /create_new_chat endpoint to do that first"}

    def add_new_chat(self, file_path='data/medquad.txt'):
        chat = Chat()
        chat.create_chat(file_path=file_path)
        self.chats[chat.chat_id] = chat
        return chat.chat_id

    def delete_chat(self, chat_id):
        if chat_id in self.chats:
            del self.chats[chat_id]
            return {'status': f'Chat with ID {chat_id} deleted'}
        else:
            abort(404, f"Chat with ID {chat_id} does not exist")
    
    def get_chats(self):
        chat_data = {}
        for chat_id, chat_instance in self.chats.items():
            chat_data[chat_id] = {
                'chat_id': chat_id,
                'history': chat_instance.history,
                'message_count': chat_instance.message_count
            }
        return chat_data

chatbot = Chatbot()

@app.route('/user_message', methods=['POST'])
def user_message():
    data = request.get_json()
    user_input = data.get('message')
    chat_id = data.get('chat_id')

    response_data = chatbot.process_query(user_input, chat_id)
    
    if request.environ.get('werkzeug.server.shutdown') is None:
        return jsonify(response_data)
    else:
        emit('bot_response', response_data)

@app.route('/delete_chat/<string:chat_id>', methods=['POST'])
def delete_chat(chat_id):
    response_data = chatbot.delete_chat(chat_id)
    return jsonify(response_data)

@app.route('/create_new_chat', methods=['POST'])
def create_new_chat():
    chat_id = chatbot.add_new_chat()
    return jsonify({'status': f"New chat created. ID: {chat_id}"})

@app.route("/get_chat_ids", methods=['GET'])
def get_chats():
    return jsonify(chatbot.get_chats())

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    socketio.run(app, debug=True)


