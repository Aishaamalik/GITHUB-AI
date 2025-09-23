from langchain.prompts import PromptTemplate
from utils import safe_json_parse, validate_json
import json

class ConflictResolver:
    def __init__(self, llm):
        self.llm = llm
        self.temperature = 0.6
        self.max_tokens = 1200

        # Conflict resolution prompt
        self.conflict_prompt = PromptTemplate(
            input_variables=["scenario"],
            template="""Analyze this Git merge conflict scenario and provide step-by-step resolution guidance:

            Scenario: {scenario}

            Provide a detailed response in the following JSON format:
            {{
                "analysis": "Brief analysis of the conflict situation",
                "steps": [
                    "Step 1: Clear description of what to do",
                    "Step 2: Next action to take",
                    "Step 3: Continue until resolved"
                ],
                "commands": [
                    "git command1",
                    "git command2",
                    "git command3"
                ],
                "tips": [
                    "Helpful tip 1",
                    "Helpful tip 2"
                ],
                "common_mistakes": [
                    "Mistake to avoid 1",
                    "Mistake to avoid 2"
                ]
            }}

            Focus on practical, actionable steps. Include specific Git commands when applicable.
            Make sure the JSON is valid and all fields are present."""
        )

        # Error troubleshooting prompt
        self.error_prompt = PromptTemplate(
            input_variables=["error_message"],
            template="""Analyze this Git or GitHub error and provide a solution:

            Error: {error_message}

            Provide a detailed response in the following JSON format:
            {{
                "error_type": "Type of error (e.g., authentication, merge, push, etc.)",
                "explanation": "What caused this error and why it occurred",
                "solution": "Step-by-step solution to fix the error",
                "commands": [
                    "git command1",
                    "git command2"
                ],
                "prevention": "How to prevent this error in the future"
            }}

            Make sure the JSON is valid and all fields are present."""
        )

        # Create chains using new LangChain syntax
        self.conflict_chain = self.conflict_prompt | self.llm
        self.error_chain = self.error_prompt | self.llm

    def update_settings(self, temperature, max_tokens):
        """Update AI settings"""
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm.temperature = temperature
        self.llm.max_tokens = max_tokens

    def resolve_conflict(self, scenario):
        """Resolve a merge conflict scenario"""
        try:
            response = self.conflict_chain.invoke({"scenario": scenario})
            parsed_data = safe_json_parse(response)

            if self._validate_conflict_data(parsed_data):
                return parsed_data
            else:
                return self._get_fallback_conflict_resolution(scenario)

        except Exception as e:
            print(f"Error resolving conflict: {e}")
            return self._get_fallback_conflict_resolution(scenario)

    def troubleshoot_error(self, error_message):
        """Troubleshoot a Git error"""
        try:
            response = self.error_chain.invoke({"error_message": error_message})
            parsed_data = safe_json_parse(response)

            if self._validate_error_data(parsed_data):
                return parsed_data
            else:
                return self._get_fallback_error_solution(error_message)

        except Exception as e:
            print(f"Error troubleshooting: {e}")
            return self._get_fallback_error_solution(error_message)

    def _validate_conflict_data(self, data):
        """Validate conflict resolution data"""
        required_fields = ["analysis", "steps", "commands", "tips", "common_mistakes"]
        return validate_json(data, required_fields)

    def _validate_error_data(self, data):
        """Validate error solution data"""
        required_fields = ["error_type", "explanation", "solution", "commands", "prevention"]
        return validate_json(data, required_fields)

    def _get_fallback_conflict_resolution(self, scenario):
        """Fallback conflict resolution"""
        return {
            "analysis": "Merge conflict detected in your repository",
            "steps": [
                "Open the conflicted file in your editor",
                "Look for conflict markers (<<<<<<<, =======, >>>>>>>)",
                "Edit the file to keep the desired changes",
                "Remove all conflict markers",
                "Stage the resolved file with 'git add'",
                "Commit the resolution with 'git commit'"
            ],
            "commands": [
                "git status",
                "git add <resolved-file>",
                "git commit -m 'Resolve merge conflict'"
            ],
            "tips": [
                "Always read both versions carefully before choosing",
                "Test your changes after resolving conflicts",
                "Use 'git diff' to see what changed"
            ],
            "common_mistakes": [
                "Not removing all conflict markers",
                "Committing without testing the resolution",
                "Not understanding what each change does"
            ]
        }

    def _get_fallback_error_solution(self, error_message):
        """Fallback error solution"""
        # Common error patterns
        error_lower = error_message.lower()

        if "permission denied" in error_lower:
            return {
                "error_type": "Permission Error",
                "explanation": "Git is unable to access the repository or file due to permission restrictions",
                "solution": "Check file permissions and ensure you have write access to the repository",
                "commands": [
                    "ls -la",
                    "chmod +x .git/hooks/*",
                    "git config --global user.name 'Your Name'",
                    "git config --global user.email 'your.email@example.com'"
                ],
                "prevention": "Ensure proper file permissions and configure Git user settings"
            }
        elif "merge conflict" in error_lower:
            return {
                "error_type": "Merge Conflict",
                "explanation": "Conflicting changes between branches that need manual resolution",
                "solution": "Resolve conflicts manually in affected files",
                "commands": [
                    "git status",
                    "git diff",
                    "git add <resolved-files>",
                    "git commit -m 'Resolve merge conflicts'"
                ],
                "prevention": "Pull changes frequently and communicate with team members"
            }
        elif "detached head" in error_lower:
            return {
                "error_type": "Detached HEAD",
                "explanation": "You're not on any branch, just at a specific commit",
                "solution": "Create a new branch or switch to an existing branch",
                "commands": [
                    "git branch new-branch-name",
                    "git checkout <branch-name>",
                    "git checkout -b new-branch-name"
                ],
                "prevention": "Always work on a branch, not directly on commits"
            }
        elif "authentication failed" in error_lower:
            return {
                "error_type": "Authentication Error",
                "explanation": "GitHub credentials are incorrect or missing",
                "solution": "Update your GitHub credentials or use a personal access token",
                "commands": [
                    "git config --global credential.helper store",
                    "git remote set-url origin https://<token>@github.com/user/repo.git"
                ],
                "prevention": "Use personal access tokens instead of passwords for GitHub"
            }
        else:
            return {
                "error_type": "Unknown Error",
                "explanation": "Unable to identify the specific error type",
                "solution": "Check Git documentation or try basic troubleshooting steps",
                "commands": [
                    "git status",
                    "git log --oneline -5",
                    "git remote -v"
                ],
                "prevention": "Keep your Git knowledge up to date and use version control best practices"
            }
