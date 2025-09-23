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
            template="""You are an expert Git tutor and DevOps engineer.
Carefully analyze the following Git merge conflict situation and give a structured, step-by-step resolution plan.

Scenario:
{scenario}

Your output must be **valid JSON** (no extra text, no explanations outside JSON).
Always include every required field, even if you need to infer or generalize.

JSON format:
{{
    "analysis": "Brief, clear explanation of what type of conflict this is and why it occurred",
    "steps": [
        "Step 1: Explain the immediate action (e.g., check status, inspect markers)",
        "Step 2: Explain how to resolve markers or choose ours/theirs",
        "Step 3: Next key action",
        "Final Step: Confirm resolution and commit"
    ],
    "commands": [
        "git status",
        "git diff",
        "git checkout --ours <file> # or --theirs",
        "git add <file>",
        "git commit -m '...' "
    ],
    "tips": [
        "Practical tip 1 (how to avoid mistakes)",
        "Practical tip 2 (when to use git mergetool or diff tools)",
        "Practical tip 3 (test before pushing)"
    ],
    "common_mistakes": [
        "Mistake 1: Forgetting to remove conflict markers",
        "Mistake 2: Committing unresolved code",
        "Mistake 3: Not regenerating lockfiles for package.json conflicts"
    ]
}}

Rules:
- Responses must be actionable and beginner-friendly.
- Always give at least 3 steps, 3 commands, 2 tips, and 2 mistakes.
- Prefer specific Git commands over vague explanations.
"""
        )

        # Error troubleshooting prompt
        self.error_prompt = PromptTemplate(
            input_variables=["error_message"],
            template="""You are a Git/GitHub troubleshooting assistant.
Analyze the following error and provide a structured, reliable solution.

Error:
{error_message}

Output strictly in **valid JSON** (no extra text outside JSON).

JSON format:
{{
    "error_type": "Categorize clearly (e.g., Authentication, Merge, Permission, Network, Detached HEAD, etc.)",
    "explanation": "Why this error happened in simple, clear terms",
    "solution": [
        "Step 1: Immediate fix",
        "Step 2: Additional required step",
        "Step 3: Verify the fix worked"
    ],
    "commands": [
        "git command1",
        "git command2",
        "shell command if needed"
    ],
    "prevention": "Concise advice on how to avoid this error in future (e.g., proper credential caching, frequent pulls)"
}}

Rules:
- Always output step-by-step solutions.
- Prefer concrete git commands.
- Keep explanations short and clear.
"""
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
        error_lower = error_message.lower()

        if "permission denied" in error_lower:
            return {
                "error_type": "Permission Error",
                "explanation": "Git is unable to access the repository or file due to permission restrictions",
                "solution": [
                    "Check file permissions",
                    "Ensure you have write access to the repository"
                ],
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
                "solution": [
                    "Open conflicted files",
                    "Resolve conflicts manually in affected files",
                    "Stage and commit resolution"
                ],
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
                "solution": [
                    "Decide if you want a new branch or to switch back",
                    "Create a new branch if needed",
                    "Checkout the desired branch"
                ],
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
                "solution": [
                    "Update your GitHub credentials",
                    "Use a personal access token if using HTTPS"
                ],
                "commands": [
                    "git config --global credential.helper store",
                    "git remote set-url origin https://<token>@github.com/user/repo.git"
                ],
                "prevention": "Use personal access tokens instead of passwords for GitHub"
            }
        elif "would be overwritten by merge" in error_lower:
            return {
                "error_type": "Local Changes Overwrite",
                "explanation": "This error occurs because you have uncommitted local changes in your working directory or staging area, and Git is trying to merge or pull changes from the remote repository. If you proceed, your local changes would be lost. The cause is typically having modified files that conflict with incoming changes from the remote branch.",
                "solution": [
                    "Option 1: Stash your changes (recommended if you want to keep them temporarily)",
                    "Check the status of your repository to see what files are modified",
                    "Stash your local changes to save them temporarily",
                    "Pull the remote changes to update your branch",
                    "Apply your stashed changes back to the working directory",
                    "Resolve any conflicts if they arise after applying the stash",
                    "Option 2: Commit your changes (if they are ready)",
                    "Stage your changes",
                    "Commit your changes with a meaningful message",
                    "Pull the remote changes",
                    "Resolve any merge conflicts if they occur",
                    "Option 3: Discard your changes (if you don't need them)",
                    "Reset your working directory to discard changes",
                    "Pull the remote changes"
                ],
                "commands": [
                    "# Option 1: Stash",
                    "git status",
                    "git stash push -m 'Stashing local changes before merge'",
                    "git pull origin <branch-name>",
                    "git stash pop",
                    "git status # Check for any conflicts after popping stash",
                    "# Option 2: Commit",
                    "git add .",
                    "git commit -m 'Commit local changes before merge'",
                    "git pull origin <branch-name>",
                    "# Option 3: Discard",
                    "git reset --hard HEAD",
                    "git pull origin <branch-name>"
                ],
                "prevention": "Always commit or stash your changes before merging or pulling to avoid overwriting your work. Regularly pull changes from the remote to stay up-to-date and reduce the likelihood of conflicts."
            }
        else:
            return {
                "error_type": "Unknown Error",
                "explanation": "Unable to identify the specific error type",
                "solution": [
                    "Check Git documentation",
                    "Try basic troubleshooting steps"
                ],
                "commands": [
                    "git status",
                    "git log --oneline -5",
                    "git remote -v"
                ],
                "prevention": "Keep your Git knowledge up to date and use version control best practices"
            }
