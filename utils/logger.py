from datetime import datetime


def log(agent: str, message: str) -> None:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] [{agent.upper()}] {message}")