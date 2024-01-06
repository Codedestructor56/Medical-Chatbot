from flask import Flask, request
from flask_socketio import SocketIO, emit
from chatbot import Chat

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

class Chatbot:
    def __init__(self):
        self.chat = None

    def process_query(self, user_input):
        try:
            response = self.chat.conversation_chat(user_input)
            return {
                'chat_id': self.chat.chat_id,
                'bot_response': response
            }
        except AttributeError as e:
            return {"error":"You haven't initialized the conversation yet, use the /create_new_chat endpoint to do that first"}
        
    def add_new_chat(self):
        self.chat = Chat()
        self.chat.create_chat(file_path='data/medquad.txt')
        return self.chat.chat_id

chatbot = Chatbot()

@app.route('/user_message', methods=['POST'])
def user_message():
    data = request.get_json()
    user_input = data.get('message')

    response_data = chatbot.process_query(user_input)
    if request.environ.get('werkzeug.server.shutdown') is None:
        return response_data
    else:
        emit('bot_response', response_data)

@app.route('/delete_chat', methods=['POST'])
def delete_chat():
    chatbot.chat.delete_chat()
    return {'status': 'Chat deleted'}

@app.route('/create_new_chat', methods=['POST'])
def create_new_chat():
    chatbot.add_new_chat()
    id= chatbot.chat.chat_id
    return {'status': f"New chat created. ID: {id}"}

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    socketio.run(app, debug=True)