# import os
# from dotenv import load_dotenv

# load_dotenv()


# class Settings:
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
#     OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

#     GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
#     GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER", "")
#     GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME", "")
#     GITHUB_BASE_BRANCH = os.getenv("GITHUB_BASE_BRANCH", "main")

#     SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
#     SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "")

#     RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
#     RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "")
#     RESEND_TO_EMAIL = os.getenv("RESEND_TO_EMAIL", "")

#     SKILLSYNC_API_BASE_URL = os.getenv("SKILLSYNC_API_BASE_URL", "http://127.0.0.1:8000")

#     @classmethod
#     def validate(cls) -> None:
#         required = {
#             "OPENAI_API_KEY": cls.OPENAI_API_KEY,
#             "GITHUB_TOKEN": cls.GITHUB_TOKEN,
#             "GITHUB_REPO_OWNER": cls.GITHUB_REPO_OWNER,
#             "GITHUB_REPO_NAME": cls.GITHUB_REPO_NAME,
#             "SLACK_BOT_TOKEN": cls.SLACK_BOT_TOKEN,
#             "SLACK_CHANNEL_ID": cls.SLACK_CHANNEL_ID,
#             "RESEND_API_KEY": cls.RESEND_API_KEY,
#             "RESEND_FROM_EMAIL": cls.RESEND_FROM_EMAIL,
#             "RESEND_TO_EMAIL": cls.RESEND_TO_EMAIL,
#         }
#         missing = [k for k, v in required.items() if not v]
#         if missing:
#             raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER", "")
    GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME", "")
    GITHUB_BASE_BRANCH = os.getenv("GITHUB_BASE_BRANCH", "main")

    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "")

    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "")
    RESEND_TO_EMAIL = os.getenv("RESEND_TO_EMAIL", "")

    SKILLSYNC_API_BASE_URL = os.getenv("SKILLSYNC_API_BASE_URL", "http://127.0.0.1:8000")

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    MESSAGE_HISTORY_FILE = os.getenv("MESSAGE_HISTORY_FILE", "message_history.jsonl")

    @classmethod
    def validate(cls) -> None:
        required = {
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
            "GITHUB_TOKEN": cls.GITHUB_TOKEN,
            "GITHUB_REPO_OWNER": cls.GITHUB_REPO_OWNER,
            "GITHUB_REPO_NAME": cls.GITHUB_REPO_NAME,
            "SLACK_BOT_TOKEN": cls.SLACK_BOT_TOKEN,
            "SLACK_CHANNEL_ID": cls.SLACK_CHANNEL_ID,
            "RESEND_API_KEY": cls.RESEND_API_KEY,
            "RESEND_FROM_EMAIL": cls.RESEND_FROM_EMAIL,
            "RESEND_TO_EMAIL": cls.RESEND_TO_EMAIL,
            "REDIS_URL": cls.REDIS_URL,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")