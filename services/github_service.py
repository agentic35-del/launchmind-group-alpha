






import base64
import requests
from typing import List, Optional

from config import Settings


class GitHubService:
    def __init__(self) -> None:
        self.owner = Settings.GITHUB_REPO_OWNER
        self.repo = Settings.GITHUB_REPO_NAME
        self.base_branch = Settings.GITHUB_BASE_BRANCH
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        self.headers = {
            "Authorization": f"token {Settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }

    def _request(self, method: str, url: str, **kwargs):
        response = requests.request(method, url, headers=self.headers, timeout=60, **kwargs)
        if response.status_code >= 400:
            raise RuntimeError(f"GitHub API error {response.status_code}: {response.text}")
        if response.text:
            return response.json()
        return {}

    def get_branch_sha(self, branch: Optional[str] = None) -> str:
        branch = branch or self.base_branch
        data = self._request("GET", f"{self.base_url}/git/ref/heads/{branch}")
        return data["object"]["sha"]

    def create_branch(self, branch_name: str, from_sha: Optional[str] = None) -> None:
        sha = from_sha or self.get_branch_sha()
        self._request(
            "POST",
            f"{self.base_url}/git/refs",
            json={"ref": f"refs/heads/{branch_name}", "sha": sha},
        )

    def create_issue(self, title: str, body: str) -> str:
        data = self._request("POST", f"{self.base_url}/issues", json={"title": title, "body": body})
        return data["html_url"]

    def create_or_update_file(self, branch_name: str, path: str, content: str, message: str) -> str:
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        existing_sha = None
        try:
            existing = self._request(
                "GET",
                f"{self.base_url}/contents/{path}?ref={branch_name}",
            )
            existing_sha = existing.get("sha")
        except Exception:
            existing_sha = None

        payload = {
            "message": message,
            "content": encoded,
            "branch": branch_name,
            "committer": {
                "name": "EngineerAgent",
                "email": "agent@launchmind.ai",
            },
            "author": {
                "name": "EngineerAgent",
                "email": "agent@launchmind.ai",
            },
        }

        if existing_sha:
            payload["sha"] = existing_sha

        data = self._request("PUT", f"{self.base_url}/contents/{path}", json=payload)
        return data["content"]["html_url"]

    def open_pull_request(self, title: str, body: str, head: str, base: Optional[str] = None) -> str:
        data = self._request(
            "POST",
            f"{self.base_url}/pulls",
            json={"title": title, "body": body, "head": head, "base": base or self.base_branch},
        )
        return data["html_url"]

    def get_pull_request(self, pr_url: str) -> dict:
        api_url = pr_url.replace("https://github.com/", "https://api.github.com/repos/").replace("/pull/", "/pulls/")
        return self._request("GET", api_url)

    def create_review_comments(self, pr_number: int, commit_id: str, comments: List[dict]) -> None:
        self._request(
            "POST",
            f"{self.base_url}/pulls/{pr_number}/reviews",
            json={
                "commit_id": commit_id,
                "body": "QA Agent review comments",
                "event": "COMMENT",
                "comments": comments,
            },
        )