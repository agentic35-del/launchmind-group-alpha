# from config import Settings
# from message_bus import MessageBus
# from services.email_service import EmailService
# from services.github_service import GitHubService
# from services.llm_service import LLMService
# from services.slack_service import SlackService
# from agents.ceo_agent import CEOAgent
# from agents.product_agent import ProductAgent
# from agents.engineer_agent import EngineerAgent
# from agents.marketing_agent import MarketingAgent
# from agents.qa_agent import QAAgent
# from utils.logger import log


# STARTUP_IDEA = """
# SkillSync is a browser extension that monitors job postings across LinkedIn, Indeed, and Glassdoor as the user browses.
# It extracts required skills from postings, compares them against the user's uploaded resume, and generates a personalized
# skills-gap report showing exactly which skills are missing and how to close those gaps.
# """.strip()


# def has_pending_messages(bus: MessageBus) -> bool:
#     return any(len(queue) > 0 for queue in bus.queues.values())


# def main() -> None:
#     Settings.validate()

#     bus = MessageBus()
#     llm = LLMService()
#     github = GitHubService()
#     slack = SlackService()
#     email = EmailService()

#     ceo = CEOAgent("ceo", bus, llm, slack)
#     product = ProductAgent("product", bus, llm)
#     engineer = EngineerAgent("engineer", bus, llm, github)
#     marketing = MarketingAgent("marketing", bus, llm, email, slack)
#     qa = QAAgent("qa", bus, llm, github)

#     ceo.start(STARTUP_IDEA)

#     running = True
#     safety_counter = 0
#     max_loops = 60

#     while running and safety_counter < max_loops:
#         safety_counter += 1

#         product.run_once()
#         engineer.run_once()
#         marketing.run_once()
#         qa.run_once()

#         while bus.queues.get("ceo"):
#             running = ceo.handle_messages(STARTUP_IDEA)
#             if not running:
#                 break

#         if not running:
#             break

#         if not has_pending_messages(bus):
#             break

#     bus.dump_history()
#     log("main", "Execution complete. Message history saved to message_history.json")


# if __name__ == "__main__":
#     main()





from config import Settings
from message_bus import RedisMessageBus
from services.email_service import EmailService
from services.github_service import GitHubService
from services.llm_service import LLMService
from services.slack_service import SlackService
from agents.ceo_agent import CEOAgent
from agents.product_agent import ProductAgent
from agents.engineer_agent import EngineerAgent
from agents.marketing_agent import MarketingAgent
from agents.qa_agent import QAAgent
from utils.logger import log


STARTUP_IDEA = """
SkillSync is a browser extension that monitors job postings across LinkedIn, Indeed, and Glassdoor as the user browses.
It extracts required skills from postings, compares them against the user's uploaded resume, and generates a personalized
skills-gap report showing exactly which skills are missing and how to close those gaps.
""".strip()


def main() -> None:
    Settings.validate()

    bus = RedisMessageBus(
        redis_url=Settings.REDIS_URL,
        history_file=Settings.MESSAGE_HISTORY_FILE,
    )

    llm = LLMService()
    github = GitHubService()
    slack = SlackService()
    email = EmailService()

    ceo = CEOAgent("ceo", bus, llm, slack)
    product = ProductAgent("product", bus, llm)
    engineer = EngineerAgent("engineer", bus, llm, github)
    marketing = MarketingAgent("marketing", bus, llm, email, slack)
    qa = QAAgent("qa", bus, llm, github)

    ceo.start(STARTUP_IDEA)

    running = True
    safety_counter = 0
    max_loops = 120

    while running and safety_counter < max_loops:
        safety_counter += 1

        product.run_once()
        engineer.run_once()
        marketing.run_once()
        qa.run_once()
        running = ceo.handle_messages(STARTUP_IDEA)

    log("main", f"Execution complete. Message history saved to {Settings.MESSAGE_HISTORY_FILE}")


if __name__ == "__main__":
    main()