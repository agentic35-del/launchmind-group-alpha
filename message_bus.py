# import json
# import uuid
# from datetime import datetime, timezone
# from typing import Dict, List, Optional

# from models import AgentMessage


# class MessageBus:
#     def __init__(self) -> None:
#         self.queues: Dict[str, List[dict]] = {
#             "ceo": [],
#             "product": [],
#             "engineer": [],
#             "marketing": [],
#             "qa": [],
#         }
#         self.history: List[dict] = []

#     def build_message(
#         self,
#         from_agent: str,
#         to_agent: str,
#         message_type: str,
#         payload: dict,
#         parent_message_id: Optional[str] = None,
#     ) -> dict:
#         msg = AgentMessage(
#             message_id=str(uuid.uuid4()),
#             from_agent=from_agent,
#             to_agent=to_agent,
#             message_type=message_type,
#             payload=payload,
#             timestamp=datetime.now(timezone.utc).isoformat(),
#             parent_message_id=parent_message_id,
#         )
#         return msg.model_dump()

#     def send_message(self, message: dict) -> None:
#         recipient = message["to_agent"]
#         if recipient not in self.queues:
#             self.queues[recipient] = []
#         self.queues[recipient].append(message)
#         self.history.append(message)
#         print(f"\n[BUS] {message['from_agent']} -> {message['to_agent']} | {message['message_type']}")
#         print(json.dumps(message, indent=2))

#     def receive_message(self, agent_name: str) -> Optional[dict]:
#         queue = self.queues.get(agent_name, [])
#         if not queue:
#             return None
#         return queue.pop(0)

#     def dump_history(self, path: str = "message_history.json") -> None:
#         with open(path, "w", encoding="utf-8") as f:
#             json.dump(self.history, f, indent=2, ensure_ascii=False)



import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import redis

from models import AgentMessage


class RedisMessageBus:
    def __init__(self, redis_url: str, history_file: str) -> None:
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
        self.history_file = Path(history_file)
        self.pubsubs: Dict[str, redis.client.PubSub] = {}
        self.history: List[dict] = []

        self.history_file.touch(exist_ok=True)

    def _channel_name(self, agent_name: str) -> str:
        return f"agent:{agent_name}"

    def register_agent(self, agent_name: str) -> None:
        if agent_name in self.pubsubs:
            return

        pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(self._channel_name(agent_name))
        self.pubsubs[agent_name] = pubsub

    def build_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: dict,
        parent_message_id: Optional[str] = None,
    ) -> dict:
        msg = AgentMessage(
            message_id=str(uuid.uuid4()),
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now(timezone.utc).isoformat(),
            parent_message_id=parent_message_id,
        )
        return msg.model_dump()

    def _append_history(self, message: dict) -> None:
        self.history.append(message)
        with self.history_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(message, ensure_ascii=False) + "\n")

    def send_message(self, message: dict) -> None:
        recipient = message["to_agent"]
        channel = self._channel_name(recipient)

        self.redis_client.publish(channel, json.dumps(message, ensure_ascii=False))
        self._append_history(message)

        print(f"\n[BUS] {message['from_agent']} -> {message['to_agent']} | {message['message_type']}")
        print(json.dumps(message, indent=2, ensure_ascii=False))

    def receive_message(self, agent_name: str) -> Optional[dict]:
        if agent_name not in self.pubsubs:
            self.register_agent(agent_name)

        pubsub = self.pubsubs[agent_name]
        raw = pubsub.get_message(timeout=0.2)

        while raw:
            if raw["type"] == "message":
                return json.loads(raw["data"])
            raw = pubsub.get_message(timeout=0.2)

        return None

    def has_message(self, agent_name: str) -> bool:
        if agent_name not in self.pubsubs:
            self.register_agent(agent_name)

        pubsub = self.pubsubs[agent_name]
        raw = pubsub.get_message(timeout=0.01)

        if not raw:
            return False

        if raw["type"] == "message":
            # put it back in a temporary redis list for this process would be overkill,
            # so in our loop we should just call receive_message directly.
            # This helper is not needed in main if the loop is written correctly.
            raise RuntimeError("Use receive_message directly instead of has_message for Redis bus.")

        return False

    def dump_history(self, path: Optional[str] = None) -> None:
        output_path = Path(path) if path else self.history_file
        if output_path == self.history_file:
            return

        with output_path.open("w", encoding="utf-8") as f:
            for item in self.history:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")