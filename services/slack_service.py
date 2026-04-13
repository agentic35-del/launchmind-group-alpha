import requests

from config import Settings


class SlackService:
    def __init__(self) -> None:
        self.url = "https://slack.com/api/chat.postMessage"
        self.headers = {
            "Authorization": f"Bearer {Settings.SLACK_BOT_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        }
        self.channel_id = Settings.SLACK_CHANNEL_ID

    def post_launch_message(self, title: str, description: str, pr_url: str) -> dict:
        payload = {
            "channel": self.channel_id,
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": title},
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": description},
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*PR:* <{pr_url}|View Pull Request>"},
                        {"type": "mrkdwn", "text": "*Status:* Ready for review"},
                    ],
                },
            ],
        }
        response = requests.post(self.url, headers=self.headers, json=payload, timeout=60)
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Slack API error: {data}")
        return data

    def post_final_summary(self, summary: str) -> dict:
        payload = {
            "channel": self.channel_id,
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "LaunchMind CEO Final Summary"},
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": summary},
                },
            ],
        }
        response = requests.post(self.url, headers=self.headers, json=payload, timeout=60)
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Slack API error: {data}")
        return data