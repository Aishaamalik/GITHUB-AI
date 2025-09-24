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

        # Enhanced universal error troubleshooting prompt
        self.error_prompt = PromptTemplate(
            input_variables=["error_message"],
            template="""You are an expert Git and GitHub troubleshooting specialist with extensive knowledge of version control systems, Git internals, and GitHub's ecosystem.

Analyze the following error message and provide a comprehensive, universal solution that works for any Git or GitHub error.

Error Message:
{error_message}

**IMPORTANT**: Output ONLY valid JSON with no additional text, explanations, or formatting outside the JSON structure.

**Enhanced JSON Response Format**:
{{
    "error_category": "Primary category (e.g., Authentication, Network, Repository, Branch, Merge, Permissions, GitHub API, Local Repository, Remote Operations, etc.)",
    "error_type": "Specific error type (e.g., Invalid Credentials, Connection Timeout, Corrupted Repository, Detached HEAD, Merge Conflict, Insufficient Permissions, Rate Limit Exceeded, etc.)",
    "severity": "Critical/High/Medium/Low based on impact",
    "explanation": "Detailed explanation of what caused this error and why it occurs",
    "immediate_actions": [
        "Step 1: First immediate action to take",
        "Step 2: Second action to diagnose or fix",
        "Step 3: Third action to resolve"
    ],
    "detailed_solution": [
        "Comprehensive step-by-step solution",
        "Include all necessary commands and explanations",
        "Handle edge cases and variations"
    ],
    "commands": [
        "git command1 --flags",
        "git command2 --options",
        "shell command if needed",
        "Additional commands as required"
    ],
    "alternative_solutions": [
        "Alternative approach 1 if the main solution doesn't work",
        "Alternative approach 2 for different scenarios"
    ],
    "verification_steps": [
        "How to verify the fix worked",
        "What to check after applying the solution"
    ],
    "prevention": "How to prevent this error in the future",
    "related_errors": [
        "Similar errors that might occur",
        "How they differ from this one"
    ],
    "github_docs": "Relevant GitHub documentation links if applicable",
    "additional_resources": [
        "Helpful articles, Stack Overflow links, or tools"
    ]
}}

**Analysis Guidelines**:
- Categorize errors precisely using standard Git/GitHub terminology
- Provide multiple solution paths when applicable
- Include both Git commands and GitHub-specific solutions
- Consider different operating systems and Git versions
- Handle both local repository and remote GitHub issues
- Include troubleshooting for common edge cases

**GitHub-Specific Errors to Handle**:
- API rate limiting
- Repository permissions (read/write/admin)
- Fork and pull request issues
- GitHub Actions and workflows
- Branch protection rules
- Repository settings and configurations

**Universal Error Handling**:
- Network and connectivity issues
- Authentication and credentials
- Repository corruption and recovery
- Branch and merge conflicts
- Remote repository synchronization
- Local Git configuration problems

**Response Rules**:
- Always provide at least 3 immediate actions
- Include at least 2 alternative solutions when possible
- Provide specific, executable commands
- Keep explanations clear and actionable
- Include verification steps for each solution
- Add prevention advice for future occurrences
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
        required_fields = ["error_category", "error_type", "severity", "explanation", "immediate_actions", "detailed_solution", "commands", "alternative_solutions", "verification_steps", "prevention"]
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
        """Enhanced fallback error solution with comprehensive error database"""
        error_lower = error_message.lower()

        # Network and Connectivity Errors
        if any(keyword in error_lower for keyword in ["connection", "timeout", "network", "unreachable", "connection refused"]):
            return {
                "error_category": "Network",
                "error_type": "Connection Error",
                "severity": "High",
                "explanation": "Git is unable to connect to the remote repository due to network issues, firewall restrictions, or server unavailability",
                "immediate_actions": [
                    "Check your internet connection",
                    "Verify the remote repository URL is correct",
                    "Test connectivity to GitHub/GitLab servers"
                ],
                "detailed_solution": [
                    "Check if you can access the remote repository URL in your browser",
                    "Verify your firewall and proxy settings",
                    "Try using a different network or VPN if applicable",
                    "Check if the remote server is experiencing downtime"
                ],
                "commands": [
                    "ping github.com",
                    "curl -I https://github.com",
                    "git remote -v",
                    "git ls-remote origin",
                    "git config --global http.proxy",
                    "git config --global https.proxy"
                ],
                "alternative_solutions": [
                    "Use SSH instead of HTTPS if having authentication issues",
                    "Try cloning a different repository to isolate the problem"
                ],
                "verification_steps": [
                    "Run 'git ls-remote origin' to test connectivity",
                    "Check if 'ping github.com' works",
                    "Verify the remote URL is accessible in browser"
                ],
                "prevention": "Ensure stable internet connection and consider using SSH keys for better reliability",
                "related_errors": [
                    "Authentication failed",
                    "Repository not found",
                    "SSL certificate errors"
                ],
                "github_docs": "https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories",
                "additional_resources": [
                    "https://stackoverflow.com/questions/tagged/git-network"
                ]
            }

        # Repository Corruption Errors
        elif any(keyword in error_lower for keyword in ["corrupt", "broken", "invalid", "malformed", "repository", "index"]):
            return {
                "error_category": "Repository",
                "error_type": "Repository Corruption",
                "severity": "Critical",
                "explanation": "The Git repository has become corrupted, possibly due to disk issues, interrupted operations, or file system problems",
                "immediate_actions": [
                    "Stop all Git operations immediately",
                    "Make a backup of the entire repository",
                    "Check for any obvious file system issues"
                ],
                "detailed_solution": [
                    "Create a backup of your repository",
                    "Check the integrity of the Git objects",
                    "Attempt to repair the repository using git fsck",
                    "If repair fails, recover from remote or reflog"
                ],
                "commands": [
                    "cp -r . /path/to/backup",
                    "git fsck --full",
                    "git reflog",
                    "git reset --hard HEAD~1",
                    "git clean -fd",
                    "git gc --aggressive --prune=now"
                ],
                "alternative_solutions": [
                    "Clone the repository from remote and copy your changes",
                    "Use git reflog to recover lost commits"
                ],
                "verification_steps": [
                    "Run 'git status' to see if repository is accessible",
                    "Check 'git fsck' output for errors",
                    "Verify all branches are intact"
                ],
                "prevention": "Regularly backup your repository and avoid interrupting Git operations",
                "related_errors": [
                    "Index corruption",
                    "Object database corruption",
                    "Reflog corruption"
                ],
                "github_docs": "https://docs.github.com/en/get-started/getting-started-with-git/about-git",
                "additional_resources": [
                    "https://git-scm.com/docs/git-fsck"
                ]
            }

        # Branch Issues
        elif any(keyword in error_lower for keyword in ["branch", "detached head", "head", "ref"]):
            return {
                "error_category": "Branch",
                "error_type": "Branch Management Error",
                "severity": "Medium",
                "explanation": "Issues related to Git branches, including detached HEAD state, branch conflicts, or reference problems",
                "immediate_actions": [
                    "Check current branch status",
                    "Identify if you're in detached HEAD state",
                    "List all available branches"
                ],
                "detailed_solution": [
                    "Determine your current Git state",
                    "If in detached HEAD, decide whether to create a branch or switch back",
                    "Clean up any unwanted branches",
                    "Ensure branch references are correct"
                ],
                "commands": [
                    "git status",
                    "git branch -a",
                    "git log --oneline -5",
                    "git checkout -b new-branch-name",
                    "git branch -d branch-name",
                    "git reflog"
                ],
                "alternative_solutions": [
                    "Use git reflog to recover lost branch references",
                    "Create a new branch from current commit"
                ],
                "verification_steps": [
                    "Run 'git branch' to see current branch",
                    "Check 'git status' for any issues",
                    "Verify you can switch between branches"
                ],
                "prevention": "Always work on named branches and avoid detached HEAD when possible",
                "related_errors": [
                    "Invalid reference",
                    "Branch not found",
                    "HEAD detached"
                ],
                "github_docs": "https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches",
                "additional_resources": [
                    "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell"
                ]
            }

        # GitHub API and Rate Limiting
        elif any(keyword in error_lower for keyword in ["api", "rate limit", "limit exceeded", "too many requests"]):
            return {
                "error_category": "GitHub API",
                "error_type": "Rate Limit Exceeded",
                "severity": "Medium",
                "explanation": "GitHub API rate limits have been exceeded, preventing Git operations that require API calls",
                "immediate_actions": [
                    "Check your current rate limit status",
                    "Wait for rate limit reset",
                    "Use alternative authentication methods"
                ],
                "detailed_solution": [
                    "Check your current API usage",
                    "Wait for the rate limit to reset (typically 1 hour)",
                    "Use a personal access token with higher limits",
                    "Consider using SSH instead of HTTPS for some operations"
                ],
                "commands": [
                    "curl -H 'Authorization: token YOUR_TOKEN' https://api.github.com/rate_limit",
                    "git config --global credential.helper",
                    "git remote set-url origin git@github.com:user/repo.git",
                    "gh auth status"
                ],
                "alternative_solutions": [
                    "Use GitHub CLI (gh) for authenticated operations",
                    "Switch to SSH authentication for higher rate limits"
                ],
                "verification_steps": [
                    "Check rate limit status with GitHub API",
                    "Verify authentication method",
                    "Test a simple git operation"
                ],
                "prevention": "Use personal access tokens and consider SSH authentication for higher rate limits",
                "related_errors": [
                    "Authentication required",
                    "API quota exceeded",
                    "Repository access denied"
                ],
                "github_docs": "https://docs.github.com/en/rest/overview/resources-in-the-rest-api?apiVersion=2022-11-28#rate-limiting",
                "additional_resources": [
                    "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github"
                ]
            }

        # Permission and Access Issues
        elif any(keyword in error_lower for keyword in ["permission", "access denied", "forbidden", "unauthorized"]):
            return {
                "error_category": "Permissions",
                "error_type": "Access Denied",
                "severity": "High",
                "explanation": "Insufficient permissions to access the repository or perform the requested operation",
                "immediate_actions": [
                    "Check your repository permissions",
                    "Verify your authentication credentials",
                    "Contact repository administrator if needed"
                ],
                "detailed_solution": [
                    "Verify your access level to the repository",
                    "Check if you have the necessary permissions for the operation",
                    "Update your authentication method if required",
                    "Contact the repository owner for access"
                ],
                "commands": [
                    "git remote -v",
                    "ssh -T git@github.com",
                    "git config --global user.name",
                    "git config --global user.email",
                    "gh auth status"
                ],
                "alternative_solutions": [
                    "Fork the repository if you need to make changes",
                    "Request access from the repository administrator"
                ],
                "verification_steps": [
                    "Check repository permissions on GitHub web interface",
                    "Verify SSH key is properly configured",
                    "Test access with a simple git operation"
                ],
                "prevention": "Ensure you have appropriate repository permissions before starting work",
                "related_errors": [
                    "Repository not found",
                    "Authentication failed",
                    "Push access denied"
                ],
                "github_docs": "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/about-permissions-for-github-apps",
                "additional_resources": [
                    "https://docs.github.com/en/get-started/learning-about-github/access-permissions-on-github"
                ]
            }

        # Original error patterns (keeping existing ones)
        if "permission denied" in error_lower:
            return {
                "error_category": "Permissions",
                "error_type": "Permission Error",
                "severity": "High",
                "explanation": "Git is unable to access the repository or file due to permission restrictions",
                "immediate_actions": [
                    "Check file permissions",
                    "Ensure you have write access to the repository"
                ],
                "detailed_solution": [
                    "Check file permissions",
                    "Ensure you have write access to the repository"
                ],
                "commands": [
                    "ls -la",
                    "chmod +x .git/hooks/*",
                    "git config --global user.name 'Your Name'",
                    "git config --global user.email 'your.email@example.com'"
                ],
                "alternative_solutions": [
                    "Run commands with sudo if system permissions are the issue"
                ],
                "verification_steps": [
                    "Check if you can access the .git directory",
                    "Verify file ownership"
                ],
                "prevention": "Ensure proper file permissions and configure Git user settings",
                "related_errors": [
                    "Access denied",
                    "Write permission denied"
                ],
                "github_docs": "https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories",
                "additional_resources": []
            }
        elif "merge conflict" in error_lower:
            return {
                "error_category": "Merge",
                "error_type": "Merge Conflict",
                "severity": "Medium",
                "explanation": "Conflicting changes between branches that need manual resolution",
                "immediate_actions": [
                    "Open conflicted files",
                    "Resolve conflicts manually in affected files",
                    "Stage and commit resolution"
                ],
                "detailed_solution": [
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
                "alternative_solutions": [
                    "Use git mergetool for interactive conflict resolution"
                ],
                "verification_steps": [
                    "Check git status for remaining conflicts",
                    "Test the application after resolution"
                ],
                "prevention": "Pull changes frequently and communicate with team members",
                "related_errors": [
                    "Conflict markers present",
                    "Merge failed"
                ],
                "github_docs": "https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/about-merge-conflicts",
                "additional_resources": []
            }
        elif "detached head" in error_lower:
            return {
                "error_category": "Branch",
                "error_type": "Detached HEAD",
                "severity": "Low",
                "explanation": "You're not on any branch, just at a specific commit",
                "immediate_actions": [
                    "Decide if you want a new branch or to switch back",
                    "Create a new branch if needed",
                    "Checkout the desired branch"
                ],
                "detailed_solution": [
                    "Decide if you want a new branch or to switch back",
                    "Create a new branch if needed",
                    "Checkout the desired branch"
                ],
                "commands": [
                    "git branch new-branch-name",
                    "git checkout <branch-name>",
                    "git checkout -b new-branch-name"
                ],
                "alternative_solutions": [
                    "Use git reflog to find the branch you were on"
                ],
                "verification_steps": [
                    "Check current branch with git branch",
                    "Verify you're on the intended branch"
                ],
                "prevention": "Always work on a branch, not directly on commits",
                "related_errors": [
                    "HEAD not pointing to branch"
                ],
                "github_docs": "https://docs.github.com/en/get-started/getting-started-with-git/managing-files/adding-a-file-to-a-repository-using-the-command-line",
                "additional_resources": []
            }
        elif "authentication failed" in error_lower:
            return {
                "error_category": "Authentication",
                "error_type": "Authentication Error",
                "severity": "High",
                "explanation": "GitHub credentials are incorrect or missing",
                "immediate_actions": [
                    "Update your GitHub credentials",
                    "Use a personal access token if using HTTPS"
                ],
                "detailed_solution": [
                    "Update your GitHub credentials",
                    "Use a personal access token if using HTTPS"
                ],
                "commands": [
                    "git config --global credential.helper store",
                    "git remote set-url origin https://<token>@github.com/user/repo.git"
                ],
                "alternative_solutions": [
                    "Use SSH keys instead of HTTPS authentication"
                ],
                "verification_steps": [
                    "Test authentication with ssh -T git@github.com",
                    "Check remote URL configuration"
                ],
                "prevention": "Use personal access tokens instead of passwords for GitHub",
                "related_errors": [
                    "Invalid credentials",
                    "Access token expired"
                ],
                "github_docs": "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token",
                "additional_resources": []
            }
        elif "would be overwritten by merge" in error_lower:
            return {
                "error_category": "Merge",
                "error_type": "Local Changes Overwrite",
                "severity": "Medium",
                "explanation": "This error occurs because you have uncommitted local changes in your working directory or staging area, and Git is trying to merge or pull changes from the remote repository. If you proceed, your local changes would be lost.",
                "immediate_actions": [
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
                "detailed_solution": [
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
                "alternative_solutions": [
                    "Use git stash with specific files only"
                ],
                "verification_steps": [
                    "Check git status after each option",
                    "Verify no local changes are lost"
                ],
                "prevention": "Always commit or stash your changes before merging or pulling to avoid overwriting your work. Regularly pull changes from the remote to stay up-to-date and reduce the likelihood of conflicts.",
                "related_errors": [
                    "Local changes would be overwritten",
                    "Uncommitted changes"
                ],
                "github_docs": "https://docs.github.com/en/get-started/getting-started-with-git/managing-files/adding-a-file-to-a-repository-using-the-command-line",
                "additional_resources": []
            }
        else:
            return {
                "error_category": "Unknown",
                "error_type": "Unknown Error",
                "severity": "Medium",
                "explanation": "Unable to identify the specific error type from the message provided",
                "immediate_actions": [
                    "Check Git documentation",
                    "Try basic troubleshooting steps",
                    "Search for the error message online"
                ],
                "detailed_solution": [
                    "Check Git documentation",
                    "Try basic troubleshooting steps",
                    "Search for the error message online"
                ],
                "commands": [
                    "git status",
                    "git log --oneline -5",
                    "git remote -v"
                ],
                "alternative_solutions": [
                    "Check GitHub status page for known issues",
                    "Try the operation in a different repository"
                ],
                "verification_steps": [
                    "Check if the error persists",
                    "Try the same operation with different parameters"
                ],
                "prevention": "Keep your Git knowledge up to date and use version control best practices",
                "related_errors": [
                    "Generic Git errors",
                    "System-specific issues"
                ],
                "github_docs": "https://docs.github.com/en/get-started/getting-started-with-git/about-git",
                "additional_resources": [
                    "https://stackoverflow.com/questions/tagged/git",
                    "https://git-scm.com/docs"
                ]
            }
