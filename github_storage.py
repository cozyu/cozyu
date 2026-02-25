import os
import json
from github import Github
from github.GithubException import UnknownObjectException

class GithubStorage:
    def __init__(self, token=None, repo_name=None):
        """
        Initialize the GitHub storage connection.
        If tokens are not provided, it tries to fetch them from environment variables
        or Streamlit secrets (if running in Streamlit).
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.repo_name = repo_name or os.environ.get("REPO_NAME")
        
        try:
            import streamlit as st
            if not self.token and "GITHUB_TOKEN" in st.secrets:
                self.token = st.secrets["GITHUB_TOKEN"]
            if not self.repo_name and "REPO_NAME" in st.secrets:
                self.repo_name = st.secrets["REPO_NAME"]
        except ImportError:
            pass

        if not self.token or not self.repo_name:
            raise ValueError("GITHUB_TOKEN and REPO_NAME must be set.")

        self.gh = Github(self.token)
        self.repo = self.gh.get_repo(self.repo_name)
        self.base_path = "data"

    def _get_file_path(self, filename):
        return f"{self.base_path}/{filename}"

    def read_json(self, filename, default_data=None):
        """
        Read a JSON file from the GitHub repository.
        If the file does not exist, it will create it with `default_data`.
        """
        path = self._get_file_path(filename)
        try:
            file_content = self.repo.get_contents(path)
            content = file_content.decoded_content.decode("utf-8")
            return json.loads(content)
        except UnknownObjectException:
            # File doesn't exist, create it with default data
            if default_data is None:
                default_data = {}
            self.write_json(filename, default_data, f"Initialize {filename}")
            return default_data
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            if default_data is None:
                default_data = {}
            return default_data

    def write_json(self, filename, data, commit_message=None):
        """
        Write data to a JSON file in the GitHub repository.
        """
        path = self._get_file_path(filename)
        content = json.dumps(data, indent=4, ensure_ascii=False)
        if commit_message is None:
            commit_message = f"Update {filename}"

        try:
            file = self.repo.get_contents(path)
            self.repo.update_file(path, commit_message, content, file.sha)
        except UnknownObjectException:
            # File doesn't exist, create it
            self.repo.create_file(path, commit_message, content)
        except Exception as e:
            print(f"Error writing to {filename}: {e}")

# Helper functions to quickly access specific data files
def get_storage():
    return GithubStorage()

def load_feeds():
    storage = get_storage()
    return storage.read_json("feeds.json", default_data=[])

def save_feeds(feeds):
    storage = get_storage()
    storage.write_json("feeds.json", feeds, "Update RSS feeds")

def load_reports():
    storage = get_storage()
    return storage.read_json("reports.json", default_data={})

def save_report(date_str, report_content):
    storage = get_storage()
    reports = storage.read_json("reports.json", default_data={})
    reports[date_str] = report_content
    storage.write_json("reports.json", reports, f"Add report for {date_str}")

def load_stats():
    storage = get_storage()
    return storage.read_json("stats.json", default_data={"total_visits": 0, "daily_visits": {}})

def increment_stat(date_str):
    storage = get_storage()
    stats = storage.read_json("stats.json", default_data={"total_visits": 0, "daily_visits": {}})
    
    stats["total_visits"] = stats.get("total_visits", 0) + 1
    
    if "daily_visits" not in stats:
        stats["daily_visits"] = {}
        
    stats["daily_visits"][date_str] = stats["daily_visits"].get(date_str, 0) + 1
    
    storage.write_json("stats.json", stats, "Increment visit stats")
