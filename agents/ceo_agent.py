import json

from agents.base_agent import BaseAgent
from prompts import CEO_DECOMPOSE_SYSTEM, CEO_DECOMPOSE_USER, CEO_REVIEW_SYSTEM, CEO_REVIEW_USER
from services.slack_service import SlackService
from utils.logger import log


class CEOAgent(BaseAgent):
    def __init__(self, name, message_bus, llm, slack_service: SlackService) -> None:
        super().__init__(name, message_bus, llm)
        self.slack_service = slack_service
        self.decision_log = []
        self.product_spec = None
        self.engineer_output = None
        self.marketing_output = None
        self.revision_counts = {
            "product": 0,
            "engineer": 0,
            "marketing": 0,
            "qa": 0,
        }
        self.max_revisions_per_role = 1

    def decompose_idea(self, idea: str) -> dict:
        result = self.llm.json_response(
            CEO_DECOMPOSE_SYSTEM,
            CEO_DECOMPOSE_USER.format(idea=idea),
        )
        self.decision_log.append({"step": "decompose", "result": result})
        return result

    def review_output(self, idea: str, role: str, output: dict) -> dict:
        review = self.llm.json_response(
            CEO_REVIEW_SYSTEM,
            CEO_REVIEW_USER.format(
                idea=idea,
                role=role,
                output=json.dumps(output, indent=2, ensure_ascii=False),
            ),
        )
        self.decision_log.append({"step": f"review_{role}", "review": review})
        return review

    def can_request_revision(self, role: str) -> bool:
        return self.revision_counts.get(role, 0) < self.max_revisions_per_role

    def mark_revision(self, role: str) -> None:
        self.revision_counts[role] = self.revision_counts.get(role, 0) + 1

    def start(self, idea: str) -> None:
        log(self.name, "Starting orchestration")
        tasks = self.decompose_idea(idea)

        self.send(
            "product",
            "task",
            {
                "idea": idea,
                "focus": tasks["product_task"],
                "acceptance_criteria": tasks.get("acceptance_criteria", []),
            },
        )

    def handle_messages(self, idea: str) -> bool:
        message = self.receive()
        if not message:
            return True

        sender = message["from_agent"]
        payload = message["payload"]

        if sender == "product":
            self.product_spec = payload["product_spec"]
            review = self.review_output(idea, "product", payload)

            if review["verdict"] == "fail" and self.can_request_revision("product"):
                self.mark_revision("product")
                self.send(
                    "product",
                    "revision_request",
                    {
                        "idea": idea,
                        "focus": self.product_spec,
                        "missing_items": review.get("missing_items", []),
                        "revision_notes": review.get("revision_instruction", ""),
                    },
                    parent_message_id=message["message_id"],
                )
                return True

            log(self.name, "Product spec approved")

            self.send(
                "engineer",
                "task",
                {
                    "product_spec": self.product_spec,
                },
                parent_message_id=message["message_id"],
            )
            return True

        if sender == "engineer":
            self.engineer_output = payload
            review = self.review_output(idea, "engineer", payload)

            if review["verdict"] == "fail" and self.can_request_revision("engineer"):
                self.mark_revision("engineer")
                self.send(
                    "engineer",
                    "revision_request",
                    {
                        "product_spec": self.product_spec,
                        "revision_notes": review.get("revision_instruction", ""),
                    },
                    parent_message_id=message["message_id"],
                )
                return True

            log(self.name, "Engineer output approved")

            self.send(
                "marketing",
                "task",
                {
                    "product_spec": self.product_spec,
                    "pr_url": self.engineer_output["pr_url"],
                },
                parent_message_id=message["message_id"],
            )
            return True

        if sender == "marketing":
            self.marketing_output = payload
            review = self.review_output(idea, "marketing", payload)

            if review["verdict"] == "fail" and self.can_request_revision("marketing"):
                self.mark_revision("marketing")
                self.send(
                    "marketing",
                    "revision_request",
                    {
                        "product_spec": self.product_spec,
                        "pr_url": self.engineer_output["pr_url"],
                        "revision_notes": review.get("revision_instruction", ""),
                    },
                    parent_message_id=message["message_id"],
                )
                return True

            log(self.name, "Marketing output approved")

            self.send(
                "qa",
                "task",
                {
                    "product_spec": self.product_spec,
                    "engineer_output": self.engineer_output,
                    "marketing_output": self.marketing_output,
                },
                parent_message_id=message["message_id"],
            )
            return True

        if sender == "qa":
            qa_review = payload["qa_review"]
            self.decision_log.append({"step": "qa_review", "review": qa_review})

            if qa_review["verdict"] == "fail":
                html_issues = qa_review.get("html_issues", [])
                marketing_issues = qa_review.get("marketing_issues", [])

                sent_revision = False

                if html_issues and self.can_request_revision("engineer"):
                    self.mark_revision("engineer")
                    self.send(
                        "engineer",
                        "revision_request",
                        {
                            "product_spec": self.product_spec,
                            "revision_notes": html_issues,
                        },
                        parent_message_id=message["message_id"],
                    )
                    sent_revision = True

                if marketing_issues and self.can_request_revision("marketing"):
                    self.mark_revision("marketing")
                    self.send(
                        "marketing",
                        "revision_request",
                        {
                            "product_spec": self.product_spec,
                            "pr_url": self.engineer_output["pr_url"],
                            "revision_notes": marketing_issues,
                        },
                        parent_message_id=message["message_id"],
                    )
                    sent_revision = True

                if sent_revision:
                    return True

            summary = self.build_final_summary()
            self.slack_service.post_final_summary(summary)
            log(self.name, "Final summary posted to Slack")
            return False

        return True

    def build_final_summary(self) -> str:
        pr_url = self.engineer_output["pr_url"] if self.engineer_output else "N/A"
        issue_url = self.engineer_output["issue_url"] if self.engineer_output else "N/A"
        tagline = self.marketing_output["copy"]["tagline"] if self.marketing_output else "N/A"

        return (
            f"*Startup:* SkillSync\n"
            f"*Tagline:* {tagline}\n"
            f"*GitHub Issue:* {issue_url}\n"
            f"*GitHub PR:* {pr_url}\n"
            f"*Outcome:* Product spec generated, landing page created, outreach email sent, launch post published, and QA review completed."
        )