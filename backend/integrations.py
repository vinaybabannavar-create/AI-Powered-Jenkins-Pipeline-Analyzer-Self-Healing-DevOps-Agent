import requests
import json
import base64
from typing import Dict, Any, Tuple, Optional, List
import urllib.parse

class JenkinsClient:
    """
    Connects to Jenkins via the official REST API with username + API token authentication,
    CSRF crumb handling, job listing, console log retrieval, and build triggering.
    Falls back cleanly to Demo/Mock Jenkins if demo mode is enabled or server is offline.
    """
    def __init__(self, base_url: str, username: Optional[str] = None, api_token: Optional[str] = None, demo_mode: bool = False):
        self.base_url = base_url.rstrip("/") if base_url else "http://localhost:5000"
        self.username = username
        self.api_token = api_token
        self.demo_mode = demo_mode
        self.session = requests.Session()

        if self.username and self.api_token:
            self.session.auth = (self.username, self.api_token)

    def _get_crumb(self) -> Dict[str, str]:
        """Fetches Jenkins CSRF Crumb if enabled on the target server."""
        try:
            crumb_url = f"{self.base_url}/crumbIssuer/api/json"
            res = self.session.get(crumb_url, timeout=4)
            if res.status_code == 200:
                data = res.json()
                return {data.get("crumbRequestField", "Jenkins-Crumb"): data.get("crumb", "")}
        except Exception:
            pass
        return {}

    def test_connection(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Tests connectivity and credentials against Jenkins /api/json."""
        if self.demo_mode:
            return True, "Connected (Demo Mode Active)", {
                "version": "2.440.1 (Mock / Demo)",
                "mode": "Demo Mode",
                "jobs": ["python-flaky-tests", "docker-image-build", "kubernetes-deploy"]
            }

        try:
            url = f"{self.base_url}/api/json"
            res = self.session.get(url, timeout=6)
            if res.status_code == 200:
                data = res.json()
                version = res.headers.get("X-Jenkins", "Unknown")
                jobs = [j.get("name") for j in data.get("jobs", [])]
                return True, f"Successfully connected to Jenkins v{version}", {
                    "version": version,
                    "jobs": jobs,
                    "url": self.base_url
                }
            elif res.status_code == 401:
                return False, "Authentication failed: Invalid username or API token", {}
            elif res.status_code == 403:
                return False, "Access forbidden: Check user permissions in Jenkins", {}
            else:
                return False, f"Jenkins returned HTTP {res.status_code}", {}
        except requests.exceptions.ConnectionError:
            return False, f"Could not connect to Jenkins at {self.base_url}. Verify host and port.", {}
        except Exception as e:
            return False, f"Connection error: {str(e)}", {}

    def get_jobs(self) -> List[Dict[str, Any]]:
        """Retrieves list of jobs/pipelines from Jenkins."""
        if self.demo_mode:
            return [
                {"name": "python-flaky-tests", "color": "red", "description": "Python unit tests pipeline"},
                {"name": "docker-image-build", "color": "red", "description": "Docker container build"},
                {"name": "kubernetes-deploy", "color": "red", "description": "K8s cluster deployment"}
            ]

        try:
            url = f"{self.base_url}/api/json?tree=jobs[name,url,color,description]"
            res = self.session.get(url, timeout=8)
            if res.status_code == 200:
                return res.json().get("jobs", [])
        except Exception as e:
            print(f"Error fetching Jenkins jobs: {e}")
        return []

    def get_build_info(self, job_name: str, build_num: str = "lastBuild") -> Dict[str, Any]:
        """Fetches metadata for a build (status, duration, timestamp, stages)."""
        try:
            url = f"{self.base_url}/job/{urllib.parse.quote(job_name)}/{build_num}/api/json"
            res = self.session.get(url, timeout=8)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print(f"Error fetching build info for {job_name}: {e}")
        return {}

    def get_console_log(self, job_name: str, build_num: str = "lastBuild") -> str:
        """Fetches raw console log text for analysis."""
        try:
            url = f"{self.base_url}/job/{urllib.parse.quote(job_name)}/{build_num}/consoleText"
            res = self.session.get(url, timeout=12)
            if res.status_code == 200:
                return res.text
        except Exception as e:
            print(f"Error fetching console log for {job_name}: {e}")
        return ""

    def get_test_report(self, job_name: str, build_num: str = "lastBuild") -> Dict[str, Any]:
        """Fetches JUnit test report if available."""
        try:
            url = f"{self.base_url}/job/{urllib.parse.quote(job_name)}/{build_num}/testReport/api/json"
            res = self.session.get(url, timeout=8)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return {}

    def trigger_build(self, job_name: str, parameters: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Triggers a new build for the given pipeline.
        Returns: (success, message, build_or_queue_url)
        """
        if self.demo_mode:
            simulated_url = f"{self.base_url}/job/{job_name}/lastBuild"
            return True, f"Auto-triggered build for {job_name} (Demo Mode)", simulated_url

        try:
            headers = self._get_crumb()
            if parameters:
                endpoint = f"{self.base_url}/job/{urllib.parse.quote(job_name)}/buildWithParameters"
                res = self.session.post(endpoint, data=parameters, headers=headers, timeout=10)
            else:
                endpoint = f"{self.base_url}/job/{urllib.parse.quote(job_name)}/build"
                res = self.session.post(endpoint, headers=headers, timeout=10)

            if res.status_code in [200, 201]:
                queue_url = res.headers.get("Location", f"{self.base_url}/job/{job_name}")
                return True, f"Successfully triggered build on Jenkins", queue_url
            else:
                return False, f"Failed to trigger build (HTTP {res.status_code})", None
        except Exception as e:
            return False, f"Exception triggering build: {str(e)}", None


class GitHubClient:
    """
    Interacts with GitHub REST API to automatically open pull requests
    with automated fixes (e.g. dependency bumps, Jenkinsfile fixes).
    """
    def __init__(self, token: Optional[str] = None, repo: Optional[str] = None):
        self.token = token
        self.repo = repo  # format: "owner/repo"
        self.api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Jenkins-DevOps-Agent"
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def open_pull_request_with_fix(
        self,
        file_path: str,
        fix_content: str,
        branch_prefix: str,
        pr_title: str,
        pr_body: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Creates a new branch, commits the file fix, and opens a real PR.
        If no GitHub token is configured, returns a simulated link.
        """
        if not self.token or not self.repo or "/" not in self.repo:
            simulated_pr = f"https://github.com/mock-org/devops-pipeline/pull/{branch_prefix[-3:]}"
            return True, "Simulated PR created (Configure GitHub Token in Settings for live PRs)", simulated_pr

        try:
            # 1. Get default branch SHA
            repo_url = f"{self.api_base}/repos/{self.repo}"
            repo_res = requests.get(repo_url, headers=self.headers, timeout=6)
            if repo_res.status_code != 200:
                return False, f"GitHub Repo access error: {repo_res.status_code}", None
            
            default_branch = repo_res.json().get("default_branch", "main")
            ref_url = f"{repo_url}/git/refs/heads/{default_branch}"
            ref_res = requests.get(ref_url, headers=self.headers, timeout=6)
            if ref_res.status_code != 200:
                return False, f"Failed to fetch base branch ref", None
            
            base_sha = ref_res.json()["object"]["sha"]

            # 2. Create new branch
            import time
            new_branch = f"{branch_prefix}-{int(time.time())}"
            new_ref_url = f"{repo_url}/git/refs"
            create_branch_res = requests.post(
                new_ref_url,
                headers=self.headers,
                json={"ref": f"refs/heads/{new_branch}", "sha": base_sha},
                timeout=6
            )
            if create_branch_res.status_code not in [200, 201]:
                return False, f"Failed to create branch: {create_branch_res.text}", None

            # 3. Create or update file on the new branch
            file_url = f"{repo_url}/contents/{file_path}"
            get_file_res = requests.get(f"{file_url}?ref={new_branch}", headers=self.headers, timeout=6)
            file_sha = get_file_res.json().get("sha") if get_file_res.status_code == 200 else None

            commit_payload = {
                "message": f"fix(ci): autonomous repair for {file_path}",
                "content": base64.b64encode(fix_content.encode("utf-8")).decode("ascii"),
                "branch": new_branch
            }
            if file_sha:
                commit_payload["sha"] = file_sha

            put_file_res = requests.put(file_url, headers=self.headers, json=commit_payload, timeout=6)
            if put_file_res.status_code not in [200, 201]:
                return False, f"Failed to commit fix: {put_file_res.text}", None

            # 4. Open Pull Request
            pr_url = f"{repo_url}/pulls"
            pr_payload = {
                "title": pr_title,
                "head": new_branch,
                "base": default_branch,
                "body": pr_body
            }
            pr_res = requests.post(pr_url, headers=self.headers, json=pr_payload, timeout=8)
            if pr_res.status_code in [200, 210, 201]:
                pr_data = pr_res.json()
                html_url = pr_data.get("html_url")
                return True, f"Pull Request opened: #{pr_data.get('number')}", html_url
            else:
                return False, f"Failed to open PR: {pr_res.text}", None
        except Exception as e:
            return False, f"GitHub API error: {str(e)}", None


class JiraClient:
    """
    Interacts with Atlassian Jira Cloud REST API (v3/v2) to automatically create
    real bug tickets for Code Defects and pipeline issues.
    """
    def __init__(
        self,
        jira_url: Optional[str] = None,
        email: Optional[str] = None,
        api_token: Optional[str] = None,
        project_key: Optional[str] = "DEVOPS"
    ):
        self.jira_url = jira_url.rstrip("/") if jira_url else None
        self.email = email
        self.api_token = api_token
        self.project_key = project_key or "DEVOPS"

    def create_issue(
        self,
        summary: str,
        description: str,
        issue_type: str = "Bug"
    ) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Creates a real Jira issue via Jira REST API.
        Returns: (success, message, issue_url, issue_key)
        """
        if not self.jira_url or not self.email or not self.api_token:
            mock_key = f"{self.project_key}-104"
            mock_url = f"https://mock-company.atlassian.net/browse/{mock_key}"
            return True, f"Simulated Jira issue {mock_key} (Configure Jira in Settings for live tickets)", mock_url, mock_key

        try:
            url = f"{self.jira_url}/rest/api/2/issue"
            auth = (self.email, self.api_token)
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            payload = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": summary[:250],
                    "description": description,
                    "issuetype": {"name": issue_type}
                }
            }
            res = requests.post(url, json=payload, auth=auth, headers=headers, timeout=10)
            if res.status_code in [200, 201]:
                data = res.json()
                key = data.get("key")
                issue_url = f"{self.jira_url}/browse/{key}"
                return True, f"Jira Issue Created: {key}", issue_url, key
            else:
                return False, f"Jira API returned HTTP {res.status_code}: {res.text[:200]}", None, None
        except Exception as e:
            return False, f"Jira error: {str(e)}", None, None
