import csv
import requests
from collections import Counter
from typing import List, Tuple


class APIDataAnalyzer:
    """Fetches data from a public REST API, analyzes it, and exports a CSV report."""

    BASE_URL = "https://jsonplaceholder.typicode.com"
    TIMEOUT = 10

    def __init__(self) -> None:
        self.users: List[dict] = []
        self.posts: List[dict] = []

    def fetch(self, endpoint: str) -> List[dict]:
        """Fetch JSON data from an API endpoint with error handling."""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {endpoint}: {e}")
            return []

    def load_data(self) -> None:
        """Load users and posts from the API."""
        self.users = self.fetch("users")
        self.posts = self.fetch("posts")
        print(f"Loaded {len(self.users)} users and {len(self.posts)} posts")

    def analyze(self) -> List[Tuple[str, int, float]]:
        """Compute per-user post count and average title length."""
        user_names = {u["id"]: u["name"] for u in self.users}
        post_counts = Counter(p["userId"] for p in self.posts)

        title_lengths: dict = {}
        for post in self.posts:
            uid = post["userId"]
            title_lengths.setdefault(uid, []).append(len(post["title"]))

        rows = []
        for uid, count in post_counts.items():
            avg_len = sum(title_lengths[uid]) / len(title_lengths[uid])
            rows.append((user_names.get(uid, "Unknown"), count, round(avg_len, 2)))

        rows.sort(key=lambda r: r[2], reverse=True)
        return rows

    def export_csv(self, rows: List[Tuple[str, int, float]],
                   filename: str = "post_report.csv") -> None:
        """Write analysis results to a CSV file."""
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["User Name", "Post Count", "Avg Title Length"])
            writer.writerows(rows)
        print(f"Report saved to {filename}")

    def run(self) -> None:
        """Run the full pipeline: load, analyze, export."""
        self.load_data()
        rows = self.analyze()
        self.export_csv(rows)
        if rows:
            top = rows[0]
            print(f"Top user by avg title length: {top[0]} "
                  f"(posts: {top[1]}, avg title length: {top[2]})")


if __name__ == "__main__":
    APIDataAnalyzer().run()
