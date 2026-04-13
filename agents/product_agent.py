from agents.base_agent import BaseAgent
from prompts import PRODUCT_SYSTEM, PRODUCT_USER
from utils.logger import log


class ProductAgent(BaseAgent):
    def run_once(self) -> None:
        message = self.receive()
        if not message:
            return

        log(self.name, f"Received {message['message_type']} from {message['from_agent']}")

        payload = message["payload"]
        idea = payload["idea"]
        focus = payload["focus"]

        if isinstance(focus, dict):
            focus_text = (
                f"Title: {focus.get('title', '')}\n"
                f"Description: {focus.get('description', '')}\n"
                f"Deliverables: {focus.get('deliverables', [])}"
            )
        else:
            focus_text = str(focus)

        if message["message_type"] == "revision_request":
            revision_notes = payload.get("missing_items") or payload.get("revision_notes") or []
            focus_text += f"\n\nRevision notes: {revision_notes}"

        product_spec = self.llm.json_response(
            PRODUCT_SYSTEM,
            PRODUCT_USER.format(idea=idea, focus=focus_text),
        )

        self.send(
            "ceo",
            "result",
            {
                "product_spec": product_spec,
                "summary": "Product spec generated.",
            },
            parent_message_id=message["message_id"],
        )