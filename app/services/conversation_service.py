from app.database.redis import get_redis
from app.database.mongo import conversation_collection
from datetime import timedelta
import json
from app.utils.datetime import get_local_datetime
from app.engines.conversation import ConversationEngine


class ConversationService:
    def __init__(self):
        self.redis_client = get_redis()
        self.engines = {}

    def create_or_update_conversation(self, mobile_number: str, message: str):
        conversation_key = f"conversation:{mobile_number}"
        conversation = self.redis_client.get(conversation_key)
        if not conversation:
            # Fetch from MongoDB if not in Redis
            conversation = conversation_collection.find_one(
                {"mobile_number": mobile_number})
            if not conversation:
                conversation = {
                    "mobile_number": mobile_number,
                    "messages": []
                }
            else:
                conversation["_id"] = str(conversation["_id"])

        conversation["messages"].append({
            "message": message,
            "timestamp": get_local_datetime()
        })

        # Save conversation in Redis
        self.redis_client.setex(conversation_key, timedelta(
            minutes=5), json.dumps(conversation))

        return conversation

    def save_conversation_to_db(self, mobile_number: str):
        conversation_key = f"conversation:{mobile_number}"
        conversation = self.redis_client.get(conversation_key)
        if conversation:
            conversation = json.loads(conversation)
            conversation_id = conversation.pop("_id", None)
            if conversation_id:
                conversation_collection.update_one(
                    {"_id": conversation_id},
                    {"$set": conversation}
                )
            else:
                conversation_collection.insert_one(conversation)
            self.redis_client.delete(conversation_key)

    def give_reply(self, mobile_number: str, message: str):
        conversation = self.create_or_update_conversation(
            mobile_number, message)

        # Respond with default message
        engine = self.engines[mobile_number]
        if engine is None:
            # Todo change this to user id
            engine = ConversationEngine(self.redis_client, mobile_number)
            self.engines[mobile_number] = engine

        response = engine.reply()

        conversation["messages"].append({
            "message": response,
            "timestamp": get_local_datetime()
        })
        self.redis_client.setex(f"conversation:{mobile_number}", timedelta(
            minutes=5), json.dumps(conversation))
        return response
