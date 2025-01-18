from flask import Blueprint, jsonify, request
from .middleware import jwt_required
from .models import Chat
from datetime import datetime
from extensions import socketio

chat_bp = Blueprint('chat', __name__)

# Create a new message
@chat_bp.route('/message', methods=['POST'])
@jwt_required
def create_message():
    try:
        data = request.json
        if not data:
            return jsonify({'message': 'data is required'}), 400
        if 'to_id' not in data:
            return jsonify({'message': 'to_id is required'}), 400
        if 'message' not in data:
            return jsonify({'message': 'text message is required'}), 400

        from_id = request.current_user["id"]
        to_id = data["to_id"]
        message = data["message"]

        new_message = Chat(
            from_id=from_id,
            to_id=to_id,
            text=message,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        new_message.save()

        message_data = {
            "id": str(new_message.id),
            "from_id": new_message.from_id,
            "to_id": new_message.to_id,
            "text": new_message.text,
            "created_at": new_message.created_at.isoformat(),
            "updated_at": new_message.updated_at.isoformat()
        }

        socketio.emit(f'chat-message-{to_id}', message_data)
        return jsonify({'message': 'message sent successfully', "data": message_data}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"message": "internal server error", "error": str(e)}), 500

# Get messages
@chat_bp.route('/messages/<string:to_id>', methods=['GET'])
@jwt_required
def get_messages(to_id):
    try:
        from_id = request.current_user["id"]
        messages = Chat.objects(
            __raw__={
                "$or": [
                    {"from_id": from_id, "to_id": to_id},
                    {"from_id": to_id, "to_id": from_id}
                ]
            }
        ).order_by('-created_at')

        messages_list = [
            {
                "id": str(msg.id),
                "from_id": msg.from_id,
                "to_id": msg.to_id,
                "text": msg.text,
                "created_at": msg.created_at,
                "updated_at": msg.updated_at
            }
            for msg in messages
        ]

        return jsonify({"message": "messages fetched", "data": messages_list}), 200
    except Exception as e:
        return jsonify({"message": "internal server error", "error": str(e)}), 500

# Edit a message
@chat_bp.route('/message/<string:message_id>', methods=['PUT'])
@jwt_required
def edit_message(message_id):
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'message': 'updated message text is required'}), 400

        message = Chat.objects(id=message_id, from_id=request.current_user["id"]).first()
        if not message:
            return jsonify({"message": "message not found or unauthorized"}), 404

        message.message = data['message']
        message.updated_at = datetime.utcnow()
        message.save()

        return jsonify({'message': 'message updated successfully'}), 200
    except Exception as e:
        return jsonify({"message": "internal server error", "error": str(e)}), 500

# Delete a message
@chat_bp.route('/message/<string:message_id>', methods=['DELETE'])
@jwt_required
def delete_message(message_id):
    try:
        message = Chat.objects(id=message_id, from_id=request.current_user["id"]).first()
        if not message:
            return jsonify({"message": "message not found or unauthorized"}), 404
        
        message_id = str(message.id)
        message.delete()

        room = f'message-{message.to_id}'
        socketio.emit(f'delete-chat-message-{message.to_id}', {'deletedMessageId': message_id})

        return jsonify({'message': 'message deleted successfully'}), 200
    except Exception as e:
        return jsonify({"message": "internal server error", "error": str(e)}), 500
