import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import json
import json5
import requests
from commands import CommandHelper
from conflicts import ConflictResolver
from guide import TutorialGenerator
from chat import ChatAssistant
from utils import validate_json, safe_json_parse

# Load environment variables
load_dotenv()

class GitguyAssistant:
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file and ensure the key is set correctly.")

        # Initialize LLM
        self.llm = ChatGroq(
            api_key=self.groq_api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=1500
        )

        # Initialize modules
        self.command_helper = CommandHelper(self.llm)
        self.conflict_resolver = ConflictResolver(self.llm)
        self.tutorial_generator = TutorialGenerator(self.llm)
        self.chat_assistant = ChatAssistant(self.llm)

        # Settings
        self.explanation_temp = 0.6
        self.chat_temp = 0.7
        self.max_tokens = 1200

    def update_settings(self, explanation_temp, chat_temp, max_tokens):
        """Update AI settings"""
        self.explanation_temp = explanation_temp
        self.chat_temp = chat_temp
        self.max_tokens = max_tokens

        # Update LLM instances
        self.llm.temperature = explanation_temp
        self.llm.max_tokens = max_tokens

        # Update module settings
        self.command_helper.update_settings(explanation_temp, max_tokens)
        self.conflict_resolver.update_settings(explanation_temp, max_tokens)
        self.tutorial_generator.update_settings(explanation_temp, max_tokens)
        self.chat_assistant.update_settings(chat_temp, max_tokens)

    def get_command_help(self, command):
        """Get help for a Git command"""
        return self.command_helper.get_command_help(command)

    def resolve_conflict(self, scenario):
        """Resolve a merge conflict scenario"""
        return self.conflict_resolver.resolve_conflict(scenario)

    def get_tutorial(self, tutorial_type):
        """Get a beginner's tutorial"""
        return self.tutorial_generator.get_tutorial(tutorial_type)

    def search_tutorial(self, topic):
        """Search for tutorials on any GitHub-related topic"""
        return self.tutorial_generator.search_tutorial(topic)

    def troubleshoot_error(self, error_message):
        """Troubleshoot a Git error"""
        return self.conflict_resolver.troubleshoot_error(error_message)

    def chat_with_user(self, user_input):
        """Chat with the user about Git topics"""
        return self.chat_assistant.chat(user_input)

    def generate_cheat_sheet(self):
        """Generate a Git cheat sheet"""
        try:
            prompt = PromptTemplate(
                input_variables=[],
                template="""Generate a comprehensive Git cheat sheet in JSON format with the following structure:
                {
                    "basic_commands": [
                        {"command": "git init", "description": "Initialize a new repository", "example": "git init"},
                        ...
                    ],
                    "branching": [...],
                    "merging": [...],
                    "remote_operations": [...],
                    "undo_operations": [...]
                }
                Include at least 5 commands in each category. Make sure the JSON is valid."""
            )

            # Create chain using new LangChain syntax
            chain = prompt | self.llm
            response = chain.invoke({})

            # Parse and validate JSON
            parsed_data = safe_json_parse(response.content if hasattr(response, 'content') else str(response))
            if validate_json(parsed_data, ["basic_commands", "branching", "merging", "remote_operations", "undo_operations"]):
                return parsed_data
            else:
                # Fallback to basic cheat sheet
                return self._get_fallback_cheat_sheet()

        except Exception as e:
            print(f"Error generating cheat sheet: {e}")
            return self._get_fallback_cheat_sheet()

    def analyze_repository(self, repo_url, github_token=None):
        """Analyze a GitHub repository and provide a structured summary"""
        try:
            # Parse repository URL
            owner, repo = self._parse_repo_url(repo_url)
            if not owner or not repo:
                return {"error": "Invalid repository URL. Please provide a valid GitHub repository URL."}

            # Set up headers for API requests
            headers = {"Accept": "application/vnd.github.v3+json"}
            if github_token:
                headers["Authorization"] = f"token {github_token}"

            # Fetch repository data
            repo_data = self._fetch_repo_data(owner, repo, headers)
            commits_data = self._fetch_recent_commits(owner, repo, headers)
            issues_data = self._fetch_open_issues(owner, repo, headers)
            prs_data = self._fetch_open_prs(owner, repo, headers)
            contributors_data = self._fetch_contributors(owner, repo, headers)

            # Generate AI summary
            summary = self._generate_repo_summary(repo_data, commits_data, issues_data, prs_data, contributors_data)

            # Structure the response
            return {
                "repository": repo_data,
                "recent_commits": commits_data,
                "open_issues": issues_data,
                "open_pull_requests": prs_data,
                "top_contributors": contributors_data,
                "ai_summary": summary
            }

        except Exception as e:
            return {"error": f"Error analyzing repository: {str(e)}"}

    def _parse_repo_url(self, url):
        """Parse GitHub repository URL to extract owner and repo name"""
        try:
            # Remove trailing slashes and .git
            url = url.rstrip('/').rstrip('.git')
            # Handle different URL formats
            if 'github.com' in url:
                parts = url.split('github.com/')[-1].split('/')
                if len(parts) >= 2:
                    return parts[0], parts[1]
            return None, None
        except:
            return None, None

    def _fetch_repo_data(self, owner, repo, headers):
        """Fetch basic repository information"""
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "name": data.get("name"),
                "full_name": data.get("full_name"),
                "description": data.get("description"),
                "stars": data.get("stargazers_count"),
                "forks": data.get("forks_count"),
                "open_issues": data.get("open_issues_count"),
                "language": data.get("language"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at")
            }
        return {"error": f"Failed to fetch repo data: {response.status_code}"}

    def _fetch_recent_commits(self, owner, repo, headers):
        """Fetch recent commits"""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=5"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            commits = response.json()
            return [{"sha": c["sha"][:7], "message": c["commit"]["message"], "author": c["commit"]["author"]["name"], "date": c["commit"]["author"]["date"]} for c in commits]
        return []

    def _fetch_open_issues(self, owner, repo, headers):
        """Fetch open issues"""
        url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=open&per_page=5"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            issues = response.json()
            return [{"number": i["number"], "title": i["title"], "labels": [l["name"] for l in i.get("labels", [])], "created_at": i["created_at"]} for i in issues if "pull_request" not in i]
        return []

    def _fetch_open_prs(self, owner, repo, headers):
        """Fetch open pull requests"""
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=open&per_page=5"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            prs = response.json()
            return [{"number": p["number"], "title": p["title"], "author": p["user"]["login"], "created_at": p["created_at"]} for p in prs]
        return []

    def _fetch_contributors(self, owner, repo, headers):
        """Fetch top contributors"""
        url = f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page=5"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            contributors = response.json()
            return [{"login": c["login"], "contributions": c["contributions"], "avatar_url": c["avatar_url"]} for c in contributors]
        return []

    def _generate_repo_summary(self, repo_data, commits_data, issues_data, prs_data, contributors_data):
        """Generate AI summary of repository activity"""
        try:
            prompt = PromptTemplate(
                input_variables=["repo_data", "commits_data", "issues_data", "prs_data", "contributors_data"],
                template="""Based on the following repository data, provide a concise summary of what's happening in this GitHub repository:

Repository Info: {repo_data}
Recent Commits: {commits_data}
Open Issues: {issues_data}
Open Pull Requests: {prs_data}
Top Contributors: {contributors_data}

Provide a structured summary in JSON format with the following keys:
- overview: Brief overview of the repository
- recent_activity: Summary of recent commits and changes
- current_issues: Summary of open issues and challenges
- pull_requests: Summary of ongoing pull requests
- contributors: Summary of top contributors
- overall_health: Assessment of repository health (active/inactive, well-maintained, etc.)

Make sure the JSON is valid. Example format:
{{
  "overview": "This is a sample overview.",
  "recent_activity": "Recent commits show active development.",
  "current_issues": "There are several open issues related to bugs.",
  "pull_requests": "Ongoing pull requests are being reviewed.",
  "contributors": "Top contributors are actively involved.",
  "overall_health": "The repository is well-maintained and active."
}}"""
            )

            chain = prompt | self.llm
            response = chain.invoke({
                "repo_data": json.dumps(repo_data),
                "commits_data": json.dumps(commits_data),
                "issues_data": json.dumps(issues_data),
                "prs_data": json.dumps(prs_data),
                "contributors_data": json.dumps(contributors_data)
            })

            parsed_summary = safe_json_parse(response.content if hasattr(response, 'content') else str(response))
            if validate_json(parsed_summary, ["overview", "recent_activity", "current_issues", "pull_requests", "contributors", "overall_health"]):
                return parsed_summary
            else:
                # Fallback summary if validation fails
                return {
                    "overview": "Repository analysis completed.",
                    "recent_activity": "Recent commits indicate ongoing development.",
                    "current_issues": "Open issues are being tracked.",
                    "pull_requests": "Pull requests are under review.",
                    "contributors": "Contributors are actively involved.",
                    "overall_health": "Repository appears healthy."
                }

        except Exception as e:
            return {"error": f"Error generating summary: {str(e)}"}
