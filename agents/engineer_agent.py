# from agents.base_agent import BaseAgent
# from prompts import ENGINEER_SYSTEM, ENGINEER_USER
# from services.github_service import GitHubService
# from utils.logger import log


# class EngineerAgent(BaseAgent):
#     def __init__(self, name, message_bus, llm, github: GitHubService) -> None:
#         super().__init__(name, message_bus, llm)
#         self.github = github

#     def run_once(self) -> None:
#         message = self.receive()
#         if not message:
#             return

#         log(self.name, f"Received {message['message_type']} from {message['from_agent']}")

#         payload = message["payload"]
#         product_spec = dict(payload["product_spec"])

#         if message["message_type"] == "revision_request":
#             product_spec["revision_notes"] = payload.get("revision_notes", "")

#         output = self.llm.json_response(
#             ENGINEER_SYSTEM,
#             ENGINEER_USER.format(product_spec=product_spec),
#         )

#         branch_name = output["branch_name"]

#         try:
#             self.github.create_branch(branch_name)
#         except Exception as exc:
#             log(self.name, f"Branch create skipped or already exists: {exc}")

#         issue_url = self.github.create_issue(output["issue_title"], output["issue_body"])

#         self.github.create_or_update_file(
#             branch_name=branch_name,
#             path="index.html",
#             content=output["html"],
#             message="Add or update SkillSync landing page",
#         )

#         pr_url = None
#         try:
#             pr_url = self.github.open_pull_request(
#                 title=output["pr_title"],
#                 body=output["pr_body"],
#                 head=branch_name,
#             )
#         except Exception as exc:
#             log(self.name, f"PR create failed, likely already exists: {exc}")
#             pr_url = f"https://github.com/{self.github.owner}/{self.github.repo}/compare/{self.github.base_branch}...{branch_name}"

#         self.send(
#             "ceo",
#             "result",
#             {
#                 "issue_url": issue_url,
#                 "pr_url": pr_url,
#                 "branch_name": branch_name,
#                 "html": output["html"],
#                 "pr_title": output["pr_title"],
#             },
#             parent_message_id=message["message_id"],
#         )










from datetime import datetime, timezone

from agents.base_agent import BaseAgent
from prompts import ENGINEER_SYSTEM, ENGINEER_USER
from services.github_service import GitHubService
from utils.logger import log


class EngineerAgent(BaseAgent):
    def __init__(self, name, message_bus, llm, github: GitHubService) -> None:
        super().__init__(name, message_bus, llm)
        self.github = github

    def _build_unique_branch_name(self, branch_suffix: str) -> str:
        safe_suffix = (branch_suffix or "landing-page").strip().lower().replace("_", "-").replace(" ", "-")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"feature/{safe_suffix}-{timestamp}"

    def run_once(self) -> None:
        message = self.receive()
        if not message:
            return

        log(self.name, f"Received {message['message_type']} from {message['from_agent']}")

        payload = message["payload"]
        product_spec = dict(payload["product_spec"])

        if message["message_type"] == "revision_request":
            product_spec["revision_notes"] = payload.get("revision_notes", "")

        output = self.llm.json_response(
            ENGINEER_SYSTEM,
            ENGINEER_USER.format(product_spec=product_spec),
        )

        branch_suffix = output.get("branch_suffix", "landing-page")
        branch_name = self._build_unique_branch_name(branch_suffix)

        self.github.create_branch(branch_name)

        issue_url = self.github.create_issue(output["issue_title"], output["issue_body"])

        self.github.create_or_update_file(
            branch_name=branch_name,
            path="index.html",
            content=output["html"],
            message="Add or update SkillSync landing page",
        )

        pr_url = self.github.open_pull_request(
            title=output["pr_title"],
            body=output["pr_body"],
            head=branch_name,
        )

        self.send(
            "ceo",
            "result",
            {
                "issue_url": issue_url,
                "pr_url": pr_url,
                "branch_name": branch_name,
                "html": output["html"],
                "pr_title": output["pr_title"],
            },
            parent_message_id=message["message_id"],
        )