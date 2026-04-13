from agents.base_agent import BaseAgent
from prompts import MARKETING_SYSTEM, MARKETING_USER
from services.email_service import EmailService
from services.slack_service import SlackService
from utils.logger import log


class MarketingAgent(BaseAgent):
    def __init__(self, name, message_bus, llm, email_service: EmailService, slack_service: SlackService) -> None:
        super().__init__(name, message_bus, llm)
        self.email_service = email_service
        self.slack_service = slack_service

    def run_once(self) -> None:
        message = self.receive()
        if not message:
            return

        log(self.name, f"Received {message['message_type']} from {message['from_agent']}")

        payload = message["payload"]
        product_spec = payload["product_spec"]
        pr_url = payload["pr_url"]

        prompt_spec = dict(product_spec)
        if message["message_type"] == "revision_request":
            prompt_spec["revision_notes"] = payload.get("revision_notes", [])

        copy = self.llm.json_response(
            MARKETING_SYSTEM,
            MARKETING_USER.format(product_spec=prompt_spec, pr_url=pr_url),
        )

        email_response = self.email_service.send_email(
            subject=copy["cold_email_subject"],
            html=copy["cold_email_html"],
        )

        slack_response = self.slack_service.post_launch_message(
            title=f"New Launch: {copy['tagline']}",
            description=f"{copy['short_description']}\n\n{copy['slack_summary_line']}",
            pr_url=pr_url,
        )

        self.send(
            "ceo",
            "result",
            {
                "copy": copy,
                "email_response": email_response,
                "slack_response": slack_response,
            },
            parent_message_id=message["message_id"],
        )