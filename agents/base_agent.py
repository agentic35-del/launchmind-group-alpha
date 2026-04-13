# from typing import Any, Dict, Optional

# from message_bus import MessageBus
# from services.llm_service import LLMService


# class BaseAgent:
#     def __init__(self, name: str, message_bus: MessageBus, llm: LLMService) -> None:
#         self.name = name
#         self.message_bus = message_bus
#         self.llm = llm

#     def send(
#         self,
#         recipient: str,
#         message_type: str,
#         payload: Dict[str, Any],
#         parent_message_id: Optional[str] = None,
#     ) -> Dict[str, Any]:
#         message = self.message_bus.build_message(
#             from_agent=self.name,
#             to_agent=recipient,
#             message_type=message_type,
#             payload=payload,
#             parent_message_id=parent_message_id,
#         )
#         self.message_bus.send_message(message)
#         return message

#     def receive(self) -> Optional[Dict[str, Any]]:
#         return self.message_bus.receive_message(self.name)


from typing import Any, Dict, Optional

from services.llm_service import LLMService


class BaseAgent:
    def __init__(self, name: str, message_bus, llm: LLMService) -> None:
        self.name = name
        self.message_bus = message_bus
        self.llm = llm

        # Redis bus ke liye zaroori
        self.message_bus.register_agent(self.name)

    def send(
        self,
        recipient: str,
        message_type: str,
        payload: Dict[str, Any],
        parent_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        message = self.message_bus.build_message(
            from_agent=self.name,
            to_agent=recipient,
            message_type=message_type,
            payload=payload,
            parent_message_id=parent_message_id,
        )
        self.message_bus.send_message(message)
        return message

    def receive(self) -> Optional[Dict[str, Any]]:
        return self.message_bus.receive_message(self.name)