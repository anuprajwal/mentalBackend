from flask import Flask, jsonify, request
from firebaseConnect import db
from queryBot import get_ai_response, analyze_journal_entry
from flask_cors import CORS
from datetime import datetime, timedelta, timezone


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



@app.route('/api/save-emotion', methods=['POST'])
def save_daily_emotion():
    data = request.get_json()

    

    if not data or "date" not in data or "mood" not in data or "talk" not in data:
        return jsonify({"error": "date, mood, and talk are required"}), 400
    

    ai_response = analyze_journal_entry(data["talk"], data["mood"])

    # Reference to chat document
    chat_ref = db.collection("daily-emotion").document(data["date"])
    chat_ref.set({
        "mood": data["mood"],
        "talk": data["talk"],
        "tags": ai_response["tags"],
        "response": ai_response["response"]
    })

    return jsonify({
        "message": "Emotion saved"
    }), 200

@app.route('/api/get-emotion', methods=['GET'])
def get_weekly_emotion():
    today = datetime.now(timezone.utc)  # timezone-aware UTC
    past_week = today - timedelta(days=7)

    # Get all docs from daily-emotion
    docs = db.collection("daily-emotion").stream()

    emotion_list = []
    for doc in docs:
        try:
            # Firestore doc.id looks like 2025-09-03T15:50:50.124Z
            doc_date = datetime.fromisoformat(doc.id.replace("Z", "+00:00"))  # aware datetime
        except Exception:
            continue

        if past_week <= doc_date <= today:
            data = doc.to_dict()
            emotion_list.append({
                "date": doc_date.strftime("%Y-%m-%d"),
                "emotion": data.get("mood")
            })

    # Sort by date
    emotion_list.sort(key=lambda x: x["date"])

    return jsonify(emotion_list), 200



@app.route('/api/get-journal', methods=['GET'])
def get_all_journal():
    # Can be like ?filters=all OR ?filters=happy&filters=sad
    filter_params = request.args.getlist("filters")

    print(filter_params)

    if not filter_params or (len(filter_params) == 1 and filter_params[0] == "all"):
        filter_emotions = "all"
    else:
        filter_emotions = filter_params 

    today = datetime.now(timezone.utc)
    past_month = today - timedelta(days=30)

    docs = db.collection("daily-emotion").stream()

    journal_list = []
    for doc in docs:
        try:
            doc_date = datetime.fromisoformat(doc.id.replace("Z", "+00:00"))  # aware datetime
        except Exception:
            continue

        data = doc.to_dict()
        mood = data.get("mood")

        if past_month <= doc_date <= today:
            if filter_emotions == "all" or mood.lower() in filter_emotions:
                journal_list.append({
                    "date": doc_date.strftime("%Y-%m-%d"),
                    "time": doc_date.strftime("%H:%M"),
                    "mood": mood,
                    "talk": data.get("talk"),
                    "tags": data.get("tags"),
                    "response":data.get("response")
                })

    journal_list.sort(key=lambda x: x["date"], reverse=True)

    return jsonify(journal_list), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
