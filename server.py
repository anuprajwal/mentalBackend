from flask import Flask, jsonify, request
from firebaseConnect import db
from queryBot import get_ai_response
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)


@app.route('/users')
def get_users():
    users_ref = db.collection("users")
    docs = users_ref.stream()
    users = [{doc.id: doc.to_dict()} for doc in docs]
    return jsonify(users)

@app.route('/api/list/chats')
def get_chat_list():
    chat_list_ref = db.collection("chat-list")
    docs = chat_list_ref.stream()

    doc_names = [doc.id for doc in docs]
    return jsonify(doc_names)

@app.route("/api/create-new-chat", methods=["POST"])
def create_new_chat():
    data = request.get_json()
    data = data["message"]
    
    if not data or "chatName" not in data:
        return jsonify({"error": "chatName is required"}), 400
    
    chat_name = data["chatName"]


    db.collection("chat-list").document(chat_name).set({})


    return jsonify({"message": "Chat created", "docId": chat_name}), 201



@app.route('/api/save-chat', methods=['POST'])
def save_chat():
    data = request.get_json()

    if not data or "chatName" not in data or "userChat" not in data:
        return jsonify({"error": "chat-name is required"}), 400

    chat_name = data["chatName"]

    text = data["userChat"]

    userMsg ={
            "sender": "user",
            "text": text,
            "timestamp": datetime.utcnow()
        }

    ai_response = get_ai_response(text)

    botMsg = {
        "sender": "bot",
        "text": ai_response,
        "timestamp": datetime.utcnow()
    }
    

    # Reference to chat document
    chat_ref = db.collection("chat-list").document(chat_name)

    # Ensure chat document exists
    chat_ref.set({"chatName": chat_name}, merge=True)

    # Save message in subcollection "messages"
    chat_ref.collection("messages").add(userMsg)
    chat_ref.collection("messages").add(botMsg)
    

    return jsonify({"message": "Chat saved", "ai_response":ai_response}), 201


@app.route('/api/chat-details', methods=['GET'])
def get_chat_details():
    chat_id = request.args.get("chatId")

    if not chat_id:
        return jsonify({"error": "chatId is required"}), 400

    # Reference to chat document
    chat_ref = db.collection("chat-list").document(chat_id)
    messages_ref = chat_ref.collection("messages").order_by("timestamp")

    # Fetch messages
    docs = messages_ref.stream()
    messages = []

    for doc in docs:
        msg = doc.to_dict()
        msg["id"] = doc.id  # include docId if needed
        # Convert datetime to string for JSON safety
        if "timestamp" in msg:
            msg["timestamp"] = msg["timestamp"].isoformat()
        messages.append(msg)

    return jsonify({
        "chatId": chat_id,
        "messages": messages
    }), 200



if __name__ == '__main__':
    app.run(port=5000, debug=True)
