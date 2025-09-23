from langchain.prompts import PromptTemplate
from utils import safe_json_parse, validate_json
import json

class TutorialGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.temperature = 0.6
        self.max_tokens = 1200

        # Tutorial prompt
        self.tutorial_prompt = PromptTemplate(
            input_variables=["tutorial_type"],
            template="""Generate a beginner-friendly tutorial for: {tutorial_type}

            Provide a detailed response in the following JSON format:
            {{
                "title": "Tutorial Title",
                "description": "Brief description of what you'll learn",
                "prerequisites": ["Requirement 1", "Requirement 2"],
                "steps": [
                    {{
                        "title": "Step Title",
                        "content": "Detailed explanation of this step",
                        "commands": ["command1", "command2"],
                        "tips": ["Tip 1", "Tip 2"]
                    }},
                    {{
                        "title": "Next Step Title",
                        "content": "Explanation for next step",
                        "commands": ["command3", "command4"],
                        "tips": ["Tip 3", "Tip 4"]
                    }}
                ],
                "summary": "What you accomplished in this tutorial",
                "next_steps": ["What to learn next 1", "What to learn next 2"]
            }}

            Make sure each step is clear, actionable, and includes relevant Git commands.
            Make sure the JSON is valid and all fields are present."""
        )

        # Create chain using new LangChain syntax
        self.chain = self.tutorial_prompt | self.llm

    def update_settings(self, temperature, max_tokens):
        """Update AI settings"""
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm.temperature = temperature
        self.llm.max_tokens = max_tokens

    def get_tutorial(self, tutorial_type):
        """Get a beginner's tutorial"""
        try:
            response = self.chain.invoke({"tutorial_type": tutorial_type})
            parsed_data = safe_json_parse(response)

            if self._validate_tutorial_data(parsed_data):
                return parsed_data
            else:
                return self._get_fallback_tutorial(tutorial_type)

        except Exception as e:
            print(f"Error generating tutorial: {e}")
            return self._get_fallback_tutorial(tutorial_type)

    def _validate_tutorial_data(self, data):
        """Validate tutorial data structure"""
        required_fields = ["title", "description", "prerequisites", "steps", "summary", "next_steps"]
        if not validate_json(data, required_fields):
            return False

        # Validate steps structure
        for step in data.get("steps", []):
            if not all(key in step for key in ["title", "content", "commands", "tips"]):
                return False

        return True

    def _get_fallback_tutorial(self, tutorial_type):
        """Fallback tutorials for common types"""
        tutorials = {
            "Git Setup": {
                "title": "Setting Up Git on Your Computer",
                "description": "Learn how to install and configure Git for version control",
                "prerequisites": ["A computer with internet access", "Basic command line knowledge"],
                "steps": [
                    {
                        "title": "Install Git",
                        "content": "Download and install Git from the official website (git-scm.com) or use your package manager",
                        "commands": ["# On Windows: Download from git-scm.com", "# On macOS: brew install git", "# On Linux: sudo apt install git"],
                        "tips": ["Choose the version appropriate for your operating system", "Git is usually pre-installed on macOS and Linux"]
                    },
                    {
                        "title": "Configure Git",
                        "content": "Set up your Git username and email address which will be associated with your commits",
                        "commands": [
                            "git config --global user.name 'Your Full Name'",
                            "git config --global user.email 'your.email@example.com'"
                        ],
                        "tips": ["Use the same email you use for GitHub", "You can check your config with 'git config --list'"]
                    },
                    {
                        "title": "Verify Installation",
                        "content": "Check that Git is properly installed and configured",
                        "commands": ["git --version", "git config --global --list"],
                        "tips": ["The version command should show Git version 2.x", "Your name and email should appear in the config list"]
                    }
                ],
                "summary": "You now have Git installed and configured on your computer",
                "next_steps": ["Creating your first repository", "Learning basic Git commands"]
            },
            "Creating a Repository": {
                "title": "Creating Your First Git Repository",
                "description": "Learn how to initialize and work with a new Git repository",
                "prerequisites": ["Git installed and configured"],
                "steps": [
                    {
                        "title": "Create a Project Directory",
                        "content": "Create a new directory for your project",
                        "commands": ["mkdir my-first-repo", "cd my-first-repo"],
                        "tips": ["Choose a descriptive name for your project", "You can create this in your preferred development folder"]
                    },
                    {
                        "title": "Initialize Git Repository",
                        "content": "Turn this directory into a Git repository",
                        "commands": ["git init"],
                        "tips": ["This creates a hidden .git folder", "You only need to do this once per project"]
                    },
                    {
                        "title": "Check Repository Status",
                        "content": "See the current state of your repository",
                        "commands": ["git status"],
                        "tips": ["This will show 'nothing to commit' initially", "Git status is your best friend for understanding what's happening"]
                    }
                ],
                "summary": "You created your first Git repository and understand basic status checking",
                "next_steps": ["Making your first commit", "Adding a remote repository"]
            },
            "Making Commits": {
                "title": "Making Your First Commits",
                "description": "Learn how to stage and commit changes to your repository",
                "prerequisites": ["A Git repository initialized"],
                "steps": [
                    {
                        "title": "Create a File",
                        "content": "Create a simple file to commit",
                        "commands": ["echo 'Hello, Git!' > hello.txt"],
                        "tips": ["You can create any type of file", "This is just for demonstration"]
                    },
                    {
                        "title": "Check Status",
                        "content": "See what files have been modified",
                        "commands": ["git status"],
                        "tips": ["New files appear in red as 'untracked'", "Modified files appear in red as 'modified'"]
                    },
                    {
                        "title": "Stage the File",
                        "content": "Add the file to the staging area",
                        "commands": ["git add hello.txt"],
                        "tips": ["git add . stages all changes", "You can stage specific files or patterns"]
                    },
                    {
                        "title": "Commit the Changes",
                        "content": "Create a commit with your staged changes",
                        "commands": ["git commit -m 'Add hello.txt with greeting'"],
                        "tips": ["Always write meaningful commit messages", "Use present tense in commit messages"]
                    },
                    {
                        "title": "View Commit History",
                        "content": "See your commit history",
                        "commands": ["git log --oneline"],
                        "tips": ["--oneline shows a compact view", "Each commit has a unique hash"]
                    }
                ],
                "summary": "You made your first commits and understand the staging process",
                "next_steps": ["Working with branches", "Pushing to GitHub"]
            },
            "Working with Branches": {
                "title": "Working with Git Branches",
                "description": "Learn how to create and manage branches for parallel development",
                "prerequisites": ["Basic Git knowledge", "A repository with commits"],
                "steps": [
                    {
                        "title": "View Current Branches",
                        "content": "See all branches in your repository",
                        "commands": ["git branch"],
                        "tips": ["The current branch is marked with an asterisk", "main or master is usually the default branch"]
                    },
                    {
                        "title": "Create a New Branch",
                        "content": "Create a branch for new features",
                        "commands": ["git branch feature-login"],
                        "tips": ["Use descriptive branch names", "Branch names should be lowercase with hyphens"]
                    },
                    {
                        "title": "Switch to the New Branch",
                        "content": "Move to the new branch to work on it",
                        "commands": ["git checkout feature-login"],
                        "tips": ["You can create and switch in one command: git checkout -b branch-name", "Always create a branch for new features"]
                    },
                    {
                        "title": "Make Changes on the Branch",
                        "content": "Add and commit changes on your branch",
                        "commands": ["git add .", "git commit -m 'Implement login feature'"],
                        "tips": ["Keep commits small and focused", "Test your changes before committing"]
                    },
                    {
                        "title": "Merge Back to Main",
                        "content": "Merge your feature branch back to main",
                        "commands": ["git checkout main", "git merge feature-login"],
                        "tips": ["Always merge into main, not the other way around", "Delete feature branches after merging"]
                    }
                ],
                "summary": "You learned how to create, work with, and merge branches",
                "next_steps": ["Resolving merge conflicts", "Collaborating with others"]
            },
            "Pushing to GitHub": {
                "title": "Pushing Your Code to GitHub",
                "description": "Learn how to connect your local repository to GitHub and push your code",
                "prerequisites": ["A Git repository", "GitHub account"],
                "steps": [
                    {
                        "title": "Create a GitHub Repository",
                        "content": "Create a new repository on GitHub.com",
                        "commands": ["# Do this on GitHub website"],
                        "tips": ["Choose a descriptive repository name", "Make it public or private as needed"]
                    },
                    {
                        "title": "Add GitHub as Remote",
                        "content": "Connect your local repo to GitHub",
                        "commands": ["git remote add origin https://github.com/yourusername/yourrepo.git"],
                        "tips": ["Replace with your actual GitHub username and repo name", "You can check remotes with 'git remote -v'"]
                    },
                    {
                        "title": "Push to GitHub",
                        "content": "Upload your commits to GitHub",
                        "commands": ["git push -u origin main"],
                        "tips": ["-u sets the upstream branch", "You may need to authenticate with GitHub"],
                        "commands": ["git push"],
                        "tips": ["Use this for subsequent pushes", "Git will remember the upstream branch"]
                    }
                ],
                "summary": "You connected your local repository to GitHub and pushed your code",
                "next_steps": ["Pull requests and collaboration", "Cloning repositories"]
            },
            "Collaboration Basics": {
                "title": "Collaborating with Others on GitHub",
                "description": "Learn the basics of collaborating on GitHub projects",
                "prerequisites": ["Git and GitHub setup", "Access to a shared repository"],
                "steps": [
                    {
                        "title": "Fork a Repository",
                        "content": "Create your own copy of someone else's repository",
                        "commands": ["# Do this on GitHub website"],
                        "tips": ["Forking creates a copy under your account", "This is how open source collaboration starts"]
                    },
                    {
                        "title": "Clone Your Fork",
                        "content": "Download your forked repository to work locally",
                        "commands": ["git clone https://github.com/yourusername/forked-repo.git"],
                        "tips": ["This creates a local copy of your fork", "You can now make changes locally"]
                    },
                    {
                        "title": "Create a Feature Branch",
                        "content": "Create a branch for your contribution",
                        "commands": ["git checkout -b my-feature"],
                        "tips": ["Always create a branch for new contributions", "Use descriptive branch names"]
                    },
                    {
                        "title": "Make Your Changes",
                        "content": "Implement your feature or fix",
                        "commands": ["git add .", "git commit -m 'Add my awesome feature'"],
                        "tips": ["Make meaningful commits", "Test your changes thoroughly"]
                    },
                    {
                        "title": "Push and Create Pull Request",
                        "content": "Push your changes and create a pull request on GitHub",
                        "commands": ["git push origin my-feature", "# Then create PR on GitHub website"],
                        "tips": ["Pull requests let others review your changes", "Include a clear description of what you changed"]
                    }
                ],
                "summary": "You learned the basic workflow for collaborating on GitHub projects",
                "next_steps": ["Code reviews", "Handling pull request feedback"]
            }
        }

        return tutorials.get(tutorial_type, {
            "title": "Unknown Tutorial",
            "description": "Tutorial type not found",
            "prerequisites": [],
            "steps": [],
            "summary": "Please select a valid tutorial type",
            "next_steps": []
        })
