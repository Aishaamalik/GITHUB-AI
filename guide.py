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

    def search_tutorial(self, topic):
        """Search for tutorials on any GitHub-related topic using AI generation"""
        try:
            # Always generate dynamically using prompt engineering
            # This ensures fresh, comprehensive content for any topic
            return self._generate_dynamic_tutorial(topic)

        except Exception as e:
            print(f"Error searching tutorial: {e}")
            return self._get_dynamic_fallback(topic)

    def _generate_dynamic_tutorial(self, topic):
        """Generate a tutorial dynamically for any GitHub topic"""
        try:
            # Enhanced prompt for dynamic tutorial generation
            dynamic_prompt = PromptTemplate(
                input_variables=["topic"],
                template="""Generate a comprehensive beginner-friendly tutorial for: {topic}

            This is a GitHub-related topic that the user wants to learn about. Create a detailed tutorial that covers:
            - What the topic is and why it's important
            - Prerequisites needed
            - Step-by-step instructions
            - Common use cases
            - Best practices
            - Tips and troubleshooting

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

            Make sure each step is clear, actionable, and includes relevant Git/GitHub commands when applicable.
            Make sure the JSON is valid and all fields are present.
            Focus on practical, hands-on learning."""
            )

            dynamic_chain = dynamic_prompt | self.llm
            response = dynamic_chain.invoke({"topic": topic})
            parsed_data = safe_json_parse(response)

            if self._validate_tutorial_data(parsed_data):
                return parsed_data
            else:
                return self._get_dynamic_fallback(topic)

        except Exception as e:
            print(f"Error generating dynamic tutorial: {e}")
            return self._get_dynamic_fallback(topic)

    def _get_dynamic_fallback(self, topic):
        """Fallback for dynamic tutorials"""
        return {
            "title": f"Learning {topic}",
            "description": f"A beginner's guide to {topic} on GitHub",
            "prerequisites": ["Basic Git knowledge", "GitHub account"],
            "steps": [
                {
                    "title": "Introduction to " + topic,
                    "content": f"Understanding the basics of {topic} and its importance in GitHub workflows.",
                    "commands": ["# This will depend on the specific topic"],
                    "tips": [
                        f"Start with the official GitHub documentation for {topic}",
                        "Practice in a test repository first",
                        "Join GitHub communities to learn from others"
                    ]
                },
                {
                    "title": "Setting Up for " + topic,
                    "content": f"Prepare your environment and repository for working with {topic}.",
                    "commands": ["git init", "git remote add origin <repository-url>"],
                    "tips": [
                        "Always work in a dedicated branch for new features",
                        "Keep your repository clean and organized",
                        "Use descriptive commit messages"
                    ]
                },
                {
                    "title": "Implementing " + topic,
                    "content": f"Step-by-step implementation guide for {topic}.",
                    "commands": ["# Implementation steps will vary by topic"],
                    "tips": [
                        "Test your changes thoroughly",
                        "Follow best practices for the specific topic",
                        "Document your work as you go"
                    ]
                }
            ],
            "summary": f"You've learned the basics of {topic} and how to implement it in your GitHub projects.",
            "next_steps": [
                "Practice with real projects",
                "Explore advanced features",
                "Contribute to open source projects using this knowledge"
            ]
        }

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
                "description": "Learn how to install and configure Git for version control. This comprehensive guide will walk you through the entire setup process, including installation, configuration, and verification. By the end, you'll have a fully functional Git environment ready for version control.",
                "prerequisites": ["A computer with internet access", "Basic command line knowledge", "Administrative privileges for installation"],
                "steps": [
                    {
                        "title": "Download and Install Git",
                        "content": "First, you need to download and install Git on your computer. Git is available for Windows, macOS, and Linux. For Windows users, visit the official Git website to download the installer. macOS users can use Homebrew, and Linux users can use their package manager. Installation typically involves running the installer and following the on-screen instructions.",
                        "commands": [
                            "# Windows: Download installer from https://git-scm.com/download/win",
                            "# macOS: brew install git (if Homebrew is installed)",
                            "# Linux (Ubuntu/Debian): sudo apt update && sudo apt install git",
                            "# Linux (CentOS/RHEL): sudo yum install git or sudo dnf install git"
                        ],
                        "tips": [
                            "Choose the version appropriate for your operating system",
                            "Git is usually pre-installed on macOS and many Linux distributions",
                            "On Windows, the installer will ask you to choose components - you can accept the defaults",
                            "During installation, you may be asked to choose a default text editor - choose one you're comfortable with"
                        ]
                    },
                    {
                        "title": "Configure Git with Your Identity",
                        "content": "Git needs to know who you are so it can label your commits with your name and email. This information is stored globally on your computer and will be used for all your Git repositories. It's important to use the same email address that you'll use for GitHub or other Git hosting services.",
                        "commands": [
                            "git config --global user.name 'Your Full Name'",
                            "git config --global user.email 'your.email@example.com'",
                            "git config --global core.editor 'code'  # Optional: Set default editor to VS Code"
                        ],
                        "tips": [
                            "Use the same email you use for GitHub to connect your commits to your account",
                            "You can check your config with 'git config --list'",
                            "The --global flag applies the setting to all repositories on your computer",
                            "If you want to use a different editor, you can set it with git config --global core.editor 'nano' or your preferred editor"
                        ]
                    },
                    {
                        "title": "Verify Installation and Configuration",
                        "content": "Now let's verify that Git is properly installed and configured. We'll check the version and ensure your user information is set correctly. This step confirms everything is working before you start using Git.",
                        "commands": [
                            "git --version",
                            "git config --global --list",
                            "git config user.name",
                            "git config user.email"
                        ],
                        "tips": [
                            "The version command should show Git version 2.x or higher",
                            "Your name and email should appear in the config list",
                            "If you see any errors, double-check your installation",
                            "You can also test Git by running 'git help' to see the help system"
                        ]
                    },
                    {
                        "title": "Set Up SSH Keys (Optional but Recommended)",
                        "content": "While not strictly necessary for basic Git usage, setting up SSH keys makes it easier to connect to GitHub and other Git services without entering your password every time. This step is especially useful if you plan to push code to remote repositories.",
                        "commands": [
                            "ssh-keygen -t rsa -b 4096 -C 'your.email@example.com'",
                            "# Press Enter to accept default file location",
                            "# Enter a passphrase (optional but recommended)",
                            "# Start the SSH agent: eval $(ssh-agent -s)",
                            "# Add your key: ssh-add ~/.ssh/id_rsa",
                            "# Copy public key: cat ~/.ssh/id_rsa.pub"
                        ],
                        "tips": [
                            "SSH keys provide a secure way to authenticate with Git servers",
                            "You can add the public key to your GitHub account in Settings > SSH and GPG keys",
                            "Using a passphrase adds extra security to your private key",
                            "If you skip this step, you can still use HTTPS for Git operations"
                        ]
                    }
                ],
                "summary": "You now have Git installed and configured on your computer with optional SSH setup. You're ready to start creating repositories and managing version control. Remember, Git is a powerful tool that tracks changes to your files over time, allowing you to collaborate with others and maintain a history of your project.",
                "next_steps": [
                    "Creating your first repository",
                    "Learning basic Git commands like add, commit, and status",
                    "Exploring GitHub and connecting your local repositories",
                    "Understanding the difference between local and remote repositories"
                ]
            },
            "Creating a Repository": {
                "title": "Creating Your First Git Repository",
                "description": "Learn how to initialize and work with a new Git repository. This tutorial will guide you through creating a project directory, initializing Git, and understanding the basic repository structure. You'll learn what happens when you create a repository and how to check its status.",
                "prerequisites": ["Git installed and configured", "Basic command line navigation"],
                "steps": [
                    {
                        "title": "Create a Project Directory",
                        "content": "Start by creating a new directory for your project. This will be the root folder for your Git repository. Choose a descriptive name that reflects what your project is about. You can create this directory anywhere on your computer, but it's often convenient to put it in a dedicated folder for your development projects.",
                        "commands": [
                            "mkdir my-first-repo",
                            "cd my-first-repo",
                            "ls -la  # Optional: List files to see the empty directory"
                        ],
                        "tips": [
                            "Choose a descriptive name for your project (e.g., 'todo-app', 'blog-website')",
                            "You can create this in your preferred development folder like ~/projects or ~/Documents",
                            "The 'ls -la' command shows hidden files too, which will be useful later",
                            "Avoid spaces in directory names as they can complicate command line usage"
                        ]
                    },
                    {
                        "title": "Initialize Git Repository",
                        "content": "Now you'll turn this directory into a Git repository by running 'git init'. This command creates a hidden .git folder that contains all the metadata and history for your repository. The .git folder is where Git stores information about commits, branches, and the project history. You only need to do this once per project.",
                        "commands": [
                            "git init",
                            "ls -la  # Notice the new .git folder"
                        ],
                        "tips": [
                            "This creates a hidden .git folder that contains all Git metadata",
                            "You only need to do this once per project - don't run it again",
                            "The .git folder should not be edited manually",
                            "If you see 'Reinitialized existing Git repository' message, that's fine"
                        ]
                    },
                    {
                        "title": "Check Repository Status",
                        "content": "Use 'git status' to see the current state of your repository. This command is one of the most important Git commands you'll use. It tells you what files have been modified, what files are staged for commit, and what branch you're currently on. Initially, it will show that there are no commits yet and the repository is empty.",
                        "commands": [
                            "git status",
                            "git status --short  # Optional: Shorter version"
                        ],
                        "tips": [
                            "This will show 'nothing to commit' initially because there are no files yet",
                            "Git status is your best friend for understanding what's happening in your repository",
                            "Run this command frequently to see changes",
                            "The --short flag gives a more compact view of changes"
                        ]
                    },
                    {
                        "title": "Understanding the .git Folder",
                        "content": "Let's take a moment to understand what the .git folder contains. While you shouldn't edit files in .git manually, it's helpful to know what's there. The .git folder contains subdirectories for objects (where Git stores file contents), refs (branch information), and the HEAD file (which points to the current branch).",
                        "commands": [
                            "ls -la .git/",
                            "cat .git/HEAD  # Shows which branch you're on"
                        ],
                        "tips": [
                            "The .git folder contains all the metadata for your repository",
                            "Never manually edit files in .git unless you know exactly what you're doing",
                            "The HEAD file points to the current branch (usually 'ref: refs/heads/main')",
                            "Git uses SHA-1 hashes to uniquely identify objects in the repository"
                        ]
                    },
                    {
                        "title": "Configure Git to Ignore Files (Optional)",
                        "content": "Create a .gitignore file to tell Git which files it should ignore. This is useful for files like temporary files, build artifacts, or sensitive information like API keys. Common files to ignore include .DS_Store (macOS), *.pyc (Python compiled files), and node_modules (Node.js dependencies).",
                        "commands": [
                            "touch .gitignore",
                            "echo '*.pyc' >> .gitignore",
                            "echo '.DS_Store' >> .gitignore",
                            "echo 'node_modules/' >> .gitignore"
                        ],
                        "tips": [
                            "You can find .gitignore templates for your programming language on GitHub",
                            "Common patterns include temporary files, build outputs, and IDE-specific files",
                            "GitHub has a gitignore repository with templates for many languages",
                            "You can check what's ignored with 'git status --ignored'"
                        ]
                    }
                ],
                "summary": "You created your first Git repository and understand the basic structure. You learned how to initialize a repository, check its status, and understand the .git folder. You also created a .gitignore file to exclude unwanted files. This foundation will help you as you start adding files and making commits.",
                "next_steps": [
                    "Making your first commit by adding files",
                    "Learning more Git commands like add, commit, and log",
                    "Understanding the difference between working directory, staging area, and repository",
                    "Exploring Git configuration options"
                ]
            },
            "Making Commits": {
                "title": "Making Your First Commits",
                "description": "Learn how to stage and commit changes to your repository. This tutorial covers the fundamental Git workflow: creating files, checking status, staging changes, making commits, and viewing history. Understanding this process is essential for effective version control.",
                "prerequisites": ["A Git repository initialized", "Basic command line knowledge"],
                "steps": [
                    {
                        "title": "Create a File to Track",
                        "content": "Let's start by creating a simple file that we can track with Git. This could be any type of file - a text file, a script, a configuration file, or even a binary file. For this tutorial, we'll create a simple text file. You can create files using your preferred text editor or command line tools.",
                        "commands": [
                            "echo 'Hello, Git! This is my first file.' > hello.txt",
                            "echo 'print(\"Hello from Python!\")' > script.py",
                            "ls -la  # See the files you created"
                        ],
                        "tips": [
                            "You can create any type of file - Git doesn't care about file types",
                            "This is just for demonstration; in real projects, you'd create meaningful files",
                            "Use your favorite text editor (nano, vim, VS Code, etc.) if you prefer",
                            "The '>' operator creates/overwrites a file with the output of the command"
                        ]
                    },
                    {
                        "title": "Check Repository Status",
                        "content": "Now let's see what Git thinks about our new files. The 'git status' command shows the current state of your working directory and staging area. It will tell you which files are untracked (new files Git doesn't know about), which files have been modified, and which files are staged for commit. This is one of the most important commands in Git.",
                        "commands": [
                            "git status",
                            "git status --short  # Optional: More compact view"
                        ],
                        "tips": [
                            "New files appear in red as 'untracked files'",
                            "Modified files appear in red as 'modified'",
                            "Staged files appear in green as 'Changes to be committed'",
                            "Run 'git status' frequently to understand what's happening",
                            "The --short flag gives a more compact view (A for added, M for modified, etc.)"
                        ]
                    },
                    {
                        "title": "Stage Files for Commit",
                        "content": "Before you can commit files, you need to stage them using 'git add'. Staging tells Git which changes you want to include in the next commit. You can stage individual files, all files, or use patterns. The staging area (also called the index) is where you prepare your changes before committing them to the repository.",
                        "commands": [
                            "git add hello.txt",
                            "git add script.py",
                            "git add .  # Alternative: Stage all changes",
                            "git status  # Check what you've staged"
                        ],
                        "tips": [
                            "'git add .' stages all changes (new, modified, deleted files)",
                            "You can stage specific files: 'git add filename.txt'",
                            "Use 'git add -p' for interactive staging to stage parts of files",
                            "Staged files appear in green in 'git status'",
                            "You can unstage files with 'git reset HEAD filename' if needed"
                        ]
                    },
                    {
                        "title": "Make Your First Commit",
                        "content": "Now that your files are staged, you can create a commit. A commit is a snapshot of your repository at a specific point in time. Each commit has a unique identifier (SHA-1 hash), a commit message describing the changes, and metadata like author and timestamp. Good commit messages are crucial for understanding the project history.",
                        "commands": [
                            "git commit -m 'Add hello.txt and script.py - first commit'",
                            "git commit -m 'Initial commit with greeting and Python script' -m 'This adds two files to start the project'"
                        ],
                        "tips": [
                            "Always write meaningful commit messages",
                            "Use present tense in commit messages ('Add feature' not 'Added feature')",
                            "Keep the first line under 50 characters, add details in subsequent lines",
                            "You can use 'git commit' without -m to open an editor for longer messages",
                            "Each commit creates a unique hash that identifies it forever"
                        ]
                    },
                    {
                        "title": "View Commit History",
                        "content": "Let's see what our commit looks like in the Git history. The 'git log' command shows the commit history with details like commit hash, author, date, and message. This helps you understand what changes have been made over time and who made them.",
                        "commands": [
                            "git log",
                            "git log --oneline  # Compact view",
                            "git log --oneline --all  # Show all branches",
                            "git show HEAD  # Show details of the last commit"
                        ],
                        "tips": [
                            "'--oneline' shows a compact view with hash and message",
                            "Each commit has a unique 40-character SHA-1 hash",
                            "You can refer to commits by their short hash (first 7-8 characters)",
                            "'git show' displays the actual changes in a commit",
                            "Use 'git log --graph' to see a visual representation of branches"
                        ]
                    },
                    {
                        "title": "Make Additional Changes and Commits",
                        "content": "Now let's make some changes to our files and create another commit. This demonstrates the iterative nature of development with Git. You'll modify a file, stage the changes, and commit them, building on your previous work.",
                        "commands": [
                            "echo '# My Python Script' >> script.py",
                            "git status  # See the modified file",
                            "git add script.py",
                            "git commit -m 'Add comment to Python script'",
                            "git log --oneline  # See both commits"
                        ],
                        "tips": [
                            "Modified files appear as 'modified' in git status",
                            "You can stage and commit multiple times as you work",
                            "Each commit builds on the previous ones",
                            "Git tracks the complete history of all changes",
                            "Don't be afraid to make frequent, small commits"
                        ]
                    }
                ],
                "summary": "You made your first commits and understand the staging process. You learned how to create files, check status, stage changes, make commits, and view history. This fundamental workflow (edit → stage → commit) is the core of using Git for version control. Remember that commits create permanent snapshots of your project at specific points in time.",
                "next_steps": [
                    "Working with branches for parallel development",
                    "Pushing your commits to GitHub for backup and collaboration",
                    "Learning to undo changes with git reset and git revert",
                    "Understanding the difference between git add and git commit",
                    "Exploring advanced commit features like amending commits"
                ]
            },
            "Working with Branches": {
                "title": "Working with Git Branches",
                "description": "Learn how to create and manage branches for parallel development. This comprehensive tutorial covers the complete branch workflow: creating branches, switching between them, making changes, merging back to main, and understanding branch management. Branches are essential for collaborative development and feature isolation.",
                "prerequisites": ["Basic Git knowledge", "A repository with commits", "Understanding of basic Git commands"],
                "steps": [
                    {
                        "title": "View Current Branches",
                        "content": "Let's start by seeing what branches exist in your repository. The 'git branch' command lists all branches, with the current branch marked by an asterisk (*). Initially, you'll only see the main branch (often called 'main' or 'master'). Understanding your branch structure is crucial for effective development.",
                        "commands": [
                            "git branch",
                            "git branch -a  # Show all branches including remotes",
                            "git status  # Confirm current branch"
                        ],
                        "tips": [
                            "The current branch is marked with an asterisk (*)",
                            "main or master is usually the default branch",
                            "Use 'git branch -a' to see remote branches too",
                            "The default branch contains your stable, production-ready code",
                            "Always know which branch you're currently on"
                        ]
                    },
                    {
                        "title": "Create a New Branch",
                        "content": "Now let's create a new branch for developing a feature. Branches allow you to work on different features or fixes in isolation. When you create a branch, it starts with all the commits from the current branch. Choose descriptive names that indicate what the branch is for.",
                        "commands": [
                            "git branch feature-login",
                            "git branch  # Verify the new branch exists",
                            "git branch feature-user-auth  # Create another branch for comparison"
                        ],
                        "tips": [
                            "Use descriptive branch names like 'feature-login', 'bugfix-header', 'docs-update'",
                            "Branch names should be lowercase with hyphens as separators",
                            "Include a prefix like 'feature/', 'bugfix/', or 'hotfix/' for organization",
                            "Don't use spaces or special characters in branch names",
                            "Keep branch names short but descriptive"
                        ]
                    },
                    {
                        "title": "Switch to the New Branch",
                        "content": "Now switch to your new branch to start working on it. The 'git checkout' command changes your working directory to the specified branch. This means any new files or changes you make will be on this branch. You can also create and switch to a branch in one command using 'git checkout -b'.",
                        "commands": [
                            "git checkout feature-login",
                            "git status  # Confirm you're on the new branch",
                            "git branch  # See the asterisk moved to your branch"
                        ],
                        "tips": [
                            "You can create and switch in one command: 'git checkout -b branch-name'",
                            "Always create a branch for new features or bug fixes",
                            "Never work directly on the main branch",
                            "Use 'git checkout -' to quickly switch back to the previous branch",
                            "Check 'git status' after switching to confirm your location"
                        ]
                    },
                    {
                        "title": "Make Changes on the Branch",
                        "content": "Now that you're on your feature branch, make some changes and commit them. This demonstrates how branches isolate your work. Any commits you make will only affect this branch until you merge it back. This is the key benefit of branching - you can experiment and develop without affecting the main codebase.",
                        "commands": [
                            "echo 'def login_user(username, password):' > auth.py",
                            "echo '    # Login logic here' >> auth.py",
                            "git add auth.py",
                            "git commit -m 'Add basic login function'",
                            "git log --oneline  # See your commit on this branch"
                        ],
                        "tips": [
                            "Keep commits small and focused on specific changes",
                            "Test your changes before committing",
                            "Write clear, descriptive commit messages",
                            "Use 'git add -p' for interactive staging if needed",
                            "Each branch maintains its own commit history"
                        ]
                    },
                    {
                        "title": "Switch Between Branches",
                        "content": "Let's switch back to main and see that your changes aren't there, then switch back to your feature branch. This demonstrates how branches keep changes isolated. When you switch branches, Git updates your working directory to match the target branch.",
                        "commands": [
                            "git checkout main",
                            "ls  # Notice auth.py is not here",
                            "git checkout feature-login",
                            "ls  # auth.py is back"
                        ],
                        "tips": [
                            "Git automatically updates your working directory when switching branches",
                            "Uncommitted changes might prevent switching - commit or stash them first",
                            "Use 'git stash' to temporarily save uncommitted changes",
                            "Always commit your work before switching branches",
                            "Check 'git status' after switching to ensure you're in the right place"
                        ]
                    },
                    {
                        "title": "Merge Branch Back to Main",
                        "content": "Now let's merge your feature branch back into main. This integrates your changes into the main codebase. The merge process combines the commit history of both branches. After merging, you can delete the feature branch since its changes are now part of main.",
                        "commands": [
                            "git checkout main",
                            "git merge feature-login",
                            "git log --oneline  # See the merged commit",
                            "git branch -d feature-login  # Delete the branch"
                        ],
                        "tips": [
                            "Always merge into main, not the other way around",
                            "Delete feature branches after merging to keep your repository clean",
                            "Use 'git branch -D' (capital D) to force delete if needed",
                            "Consider using pull requests for merging in team environments",
                            "Test your code after merging to ensure everything works"
                        ]
                    },
                    {
                        "title": "Advanced Branch Management",
                        "content": "Let's explore some advanced branch operations. You can rename branches, see the relationship between branches, and understand the commit history. These commands help you manage complex branching scenarios.",
                        "commands": [
                            "git branch -m feature-user-auth auth-improvements  # Rename branch",
                            "git branch  # See renamed branch",
                            "git log --oneline --graph --all  # Visual branch history",
                            "git branch -r  # Show remote branches"
                        ],
                        "tips": [
                            "Use 'git branch -m' to rename branches",
                            "'git log --graph' shows a visual representation of branch relationships",
                            "Remote branches (origin/main) represent branches on GitHub",
                            "Local branches are for your work, remote branches track the server state",
                            "Keep your branch list organized and delete unused branches"
                        ]
                    }
                ],
                "summary": "You learned how to create, work with, and merge branches effectively. You understand the importance of branch isolation for development, how to switch between branches, and how to merge changes back to main. Branching is fundamental to collaborative development and allows multiple people to work on different features simultaneously without conflicts.",
                "next_steps": [
                    "Resolving merge conflicts when they occur",
                    "Collaborating with others using pull requests",
                    "Understanding remote branches and fetching from GitHub",
                    "Learning advanced Git workflows like Git Flow",
                    "Using tools like Git GUI for visual branch management"
                ]
            },
            "Pushing to GitHub": {
                "title": "Pushing Your Code to GitHub",
                "description": "Learn how to connect your local repository to GitHub and push your code. This comprehensive tutorial covers creating a GitHub repository, setting up remotes, authentication, and pushing your commits. GitHub provides a centralized location for your code, backup, and collaboration with others.",
                "prerequisites": ["A Git repository with commits", "GitHub account", "Git configured with your identity"],
                "steps": [
                    {
                        "title": "Create a GitHub Repository",
                        "content": "First, create a new repository on GitHub.com. This will be the remote location where you'll store your code. You can create repositories through the GitHub web interface. Choose a descriptive name for your repository and decide whether it should be public (visible to everyone) or private (only visible to you and collaborators).",
                        "commands": [
                            "# Do this on GitHub website: https://github.com/new",
                            "# Fill in repository name, description, and visibility settings",
                            "# Do NOT initialize with README, .gitignore, or license (since you already have a local repo)"
                        ],
                        "tips": [
                            "Choose a descriptive repository name that matches your project",
                            "Public repositories are visible to everyone and great for open source",
                            "Private repositories are only visible to you and invited collaborators",
                            "Don't initialize with README since you already have a local repository",
                            "You can always change the visibility settings later"
                        ]
                    },
                    {
                        "title": "Copy the Repository URL",
                        "content": "After creating the repository, GitHub will show you the repository URL. You'll need this URL to connect your local repository to GitHub. The URL will look like 'https://github.com/yourusername/yourrepo.git'. Make sure to copy the correct URL - GitHub provides both HTTPS and SSH options.",
                        "commands": [
                            "# Copy this from GitHub after creating the repository",
                            "# Example: https://github.com/yourusername/my-first-repo.git"
                        ],
                        "tips": [
                            "Copy the HTTPS URL if you're not using SSH keys",
                            "The URL will be shown on the repository page after creation",
                            "Make sure to include the '.git' extension at the end",
                            "Keep this URL handy for the next steps",
                            "You can always find the URL later in the repository settings"
                        ]
                    },
                    {
                        "title": "Add GitHub as Remote Origin",
                        "content": "Now connect your local repository to the GitHub repository by adding it as a remote. The 'git remote add' command creates a connection between your local repository and the remote GitHub repository. The remote is typically named 'origin' by convention. This allows you to push and pull changes between your local and remote repositories.",
                        "commands": [
                            "git remote add origin https://github.com/yourusername/yourrepo.git",
                            "git remote -v  # Verify the remote was added correctly"
                        ],
                        "tips": [
                            "Replace 'yourusername' and 'yourrepo' with your actual GitHub username and repository name",
                            "Use 'git remote -v' to verify the remote was added correctly",
                            "You can have multiple remotes, but 'origin' is the conventional name for the main one",
                            "If you make a mistake, you can remove the remote with 'git remote remove origin'",
                            "The remote stores the URL, not the actual code - that's pushed separately"
                        ]
                    },
                    {
                        "title": "Push Your Code to GitHub",
                        "content": "Now push your local commits to GitHub. The 'git push' command uploads your commits from the local repository to the remote repository. The '-u' flag sets up tracking between your local branch and the remote branch, so future pushes can be done with just 'git push'. You may need to authenticate with GitHub during this step.",
                        "commands": [
                            "git push -u origin main",
                            "git remote -v  # Confirm the upstream branch is set",
                            "git branch -vv  # See tracking information"
                        ],
                        "tips": [
                            "The '-u' flag sets up branch tracking for future pushes",
                            "You may need to enter your GitHub username and password",
                            "If using 2FA, you might need a personal access token instead of password",
                            "After the first push, you can just use 'git push' for subsequent pushes",
                            "Check the GitHub website to see your code after pushing"
                        ]
                    },
                    {
                        "title": "Verify the Push was Successful",
                        "content": "Let's verify that your code was successfully pushed to GitHub. You can check the remote repository status and view your commit history to confirm everything is synchronized. This step ensures that your local and remote repositories are in sync.",
                        "commands": [
                            "git status  # Should show 'Your branch is up to date with origin/main'",
                            "git log --oneline  # See your local commits",
                            "git branch -vv  # See tracking relationship with remote"
                        ],
                        "tips": [
                            "If you see 'Your branch is up to date', the push was successful",
                            "The tracking information shows which remote branch your local branch follows",
                            "You can visit your repository on GitHub to visually confirm the code is there",
                            "Future changes will be pushed to the same remote branch",
                            "Use 'git fetch' to get updates from remote without merging"
                        ]
                    },
                    {
                        "title": "Make Additional Commits and Push",
                        "content": "Now let's make a small change, commit it, and push it to GitHub. This demonstrates the ongoing workflow of making changes locally and syncing them to the remote repository. This is how you'll typically work: make changes, commit them locally, then push to share with others.",
                        "commands": [
                            "echo '# My Project' > README.md",
                            "git add README.md",
                            "git commit -m 'Add README with project description'",
                            "git push  # Push the new commit to GitHub"
                        ],
                        "tips": [
                            "This demonstrates the typical development workflow",
                            "Each push uploads new commits to the remote repository",
                            "GitHub will show the updated code immediately after push",
                            "You can see the commit history on GitHub's web interface",
                            "Use meaningful commit messages that describe what changed"
                        ]
                    },
                    {
                        "title": "Understanding Remote Operations",
                        "content": "Let's explore some additional remote operations that you'll use frequently. Understanding how to fetch changes from remote repositories, check remote status, and manage remote branches is important for collaborative development.",
                        "commands": [
                            "git remote -v  # List all configured remotes",
                            "git fetch origin  # Download changes from remote without merging",
                            "git branch -r  # Show remote branches",
                            "git log --oneline origin/main  # See remote commit history"
                        ],
                        "tips": [
                            "'git fetch' downloads remote changes but doesn't merge them",
                            "Use 'git pull' to fetch and merge in one command",
                            "Remote branches are prefixed with 'origin/'",
                            "You can create local branches that track remote branches",
                            "Keep your local repository in sync with remote repositories"
                        ]
                    }
                ],
                "summary": "You successfully connected your local repository to GitHub and pushed your code. You learned how to create a GitHub repository, add it as a remote, push commits, and verify the synchronization. This establishes the foundation for backing up your code, collaborating with others, and using GitHub's features like issues, pull requests, and project management.",
                "next_steps": [
                    "Learning about pull requests and code reviews",
                    "Collaborating with others by cloning repositories",
                    "Setting up continuous integration with GitHub Actions",
                    "Using GitHub Pages to host websites from your repositories",
                    "Exploring GitHub's project management features"
                ]
            },
            "Collaboration Basics": {
                "title": "Collaborating with Others on GitHub",
                "description": "Learn the basics of collaborating on GitHub projects. This comprehensive tutorial covers the complete workflow for contributing to open source projects: forking repositories, cloning your fork, making changes, creating pull requests, and understanding the collaborative development process. GitHub's collaboration features enable developers worldwide to work together on projects.",
                "prerequisites": ["Git and GitHub setup", "Understanding of basic Git commands", "A project you want to contribute to"],
                "steps": [
                    {
                        "title": "Find a Project to Contribute To",
                        "content": "First, find an open source project on GitHub that you'd like to contribute to. Look for projects with clear contribution guidelines, active maintenance, and issues labeled 'good first issue' or 'help wanted'. Popular projects often have many contributors and established workflows. Consider starting with smaller projects or those that explicitly welcome new contributors.",
                        "commands": [
                            "# Browse GitHub for interesting projects",
                            "# Look for projects with 'good first issue' labels",
                            "# Check the project's README and CONTRIBUTING.md files"
                        ],
                        "tips": [
                            "Start with projects that have clear contribution guidelines",
                            "Look for issues labeled 'good first issue' or 'help wanted'",
                            "Check if the project has a CODE_OF_CONDUCT.md file",
                            "Read the project's README and CONTRIBUTING.md thoroughly",
                            "Consider your skill level when choosing a project to contribute to"
                        ]
                    },
                    {
                        "title": "Fork the Repository",
                        "content": "Forking creates a personal copy of someone else's repository under your GitHub account. This allows you to make changes without affecting the original project. The fork becomes your own repository that you can modify freely. Forking is the standard way to contribute to open source projects on GitHub.",
                        "commands": [
                            "# Do this on GitHub website: Click the 'Fork' button",
                            "# Choose where to place the fork (usually under your account)",
                            "# Wait for GitHub to create your fork"
                        ],
                        "tips": [
                            "Forking creates a copy under your GitHub username",
                            "The fork is completely independent of the original repository",
                            "You can make any changes you want to your fork",
                            "This is how open source collaboration typically starts",
                            "Your fork will automatically track updates from the original repository"
                        ]
                    },
                    {
                        "title": "Clone Your Fork Locally",
                        "content": "Now download your forked repository to your local computer so you can work on it. The 'git clone' command creates a local copy of your fork. This gives you a full Git repository on your computer where you can make changes, create commits, and push back to GitHub.",
                        "commands": [
                            "git clone https://github.com/yourusername/forked-repo.git",
                            "cd forked-repo  # Navigate into the cloned repository",
                            "git remote -v  # Check the remote configuration"
                        ],
                        "tips": [
                            "Replace 'yourusername' and 'forked-repo' with your actual GitHub username and repository name",
                            "This creates a local copy of your fork on your computer",
                            "You can now make changes locally using your preferred tools",
                            "The clone includes the full Git history of the project",
                            "Check that the remote is set to your fork, not the original repository"
                        ]
                    },
                    {
                        "title": "Set Up Upstream Remote",
                        "content": "Add the original repository as an 'upstream' remote so you can keep your fork synchronized with the latest changes. This allows you to fetch updates from the original project and keep your fork current. Having both 'origin' (your fork) and 'upstream' (original repository) remotes is a best practice for contributors.",
                        "commands": [
                            "git remote add upstream https://github.com/original-owner/original-repo.git",
                            "git remote -v  # Verify both remotes are configured",
                            "git fetch upstream  # Get the latest changes from the original repository"
                        ],
                        "tips": [
                            "The 'upstream' remote points to the original repository",
                            "This allows you to sync your fork with the latest changes",
                            "Use 'git fetch upstream' to get updates without merging",
                            "You can see both remotes with 'git remote -v'",
                            "Keep your fork in sync with upstream to avoid conflicts"
                        ]
                    },
                    {
                        "title": "Create a Feature Branch",
                        "content": "Create a new branch for your contribution. This isolates your work from the main branch and makes it easier to manage your changes. Use a descriptive name that indicates what your contribution is about. Feature branches are the standard way to organize work when contributing to projects.",
                        "commands": [
                            "git checkout -b my-feature-branch",
                            "git branch  # Confirm you're on the new branch",
                            "git status  # Check the current status"
                        ],
                        "tips": [
                            "Always create a branch for new contributions",
                            "Use descriptive branch names like 'add-user-auth', 'fix-typo-readme', 'update-dependencies'",
                            "Branch names should be lowercase with hyphens",
                            "Don't work directly on the main branch",
                            "You can switch back to main with 'git checkout main'"
                        ]
                    },
                    {
                        "title": "Make Your Changes",
                        "content": "Now implement your feature or fix. Make sure to follow the project's coding standards, write tests if applicable, and ensure your changes work correctly. This is where you'll spend most of your time when contributing to a project. Focus on making small, focused changes that address a specific issue or add a specific feature.",
                        "commands": [
                            "# Make your changes using your preferred editor",
                            "git add .  # Stage your changes",
                            "git status  # Check what you've staged",
                            "git commit -m 'Add descriptive commit message here'"
                        ],
                        "tips": [
                            "Make meaningful, focused commits",
                            "Write clear commit messages that explain what you changed and why",
                            "Test your changes thoroughly before committing",
                            "Follow the project's coding style and conventions",
                            "If the project has tests, make sure they pass"
                        ]
                    },
                    {
                        "title": "Keep Your Branch Updated",
                        "content": "Before pushing your changes, make sure your branch is up to date with the latest changes from the original repository. This helps avoid merge conflicts and ensures your contribution works with the current state of the project. Syncing with upstream is an important step in the contribution workflow.",
                        "commands": [
                            "git fetch upstream  # Get latest changes from original repository",
                            "git checkout main  # Switch to main branch",
                            "git merge upstream/main  # Merge upstream changes into main",
                            "git checkout my-feature-branch  # Switch back to your branch",
                            "git rebase main  # Rebase your changes on top of the latest main"
                        ],
                        "tips": [
                            "Always sync with upstream before creating pull requests",
                            "Rebasing keeps your commit history clean",
                            "If there are conflicts, resolve them before proceeding",
                            "This ensures your changes work with the latest codebase",
                            "Regular syncing prevents large merge conflicts later"
                        ]
                    },
                    {
                        "title": "Push Your Changes",
                        "content": "Push your feature branch to your fork on GitHub. This uploads your commits to GitHub where you can create a pull request. The push command sends your local commits to the remote repository. After pushing, your changes will be visible on GitHub.",
                        "commands": [
                            "git push origin my-feature-branch",
                            "git branch -vv  # Check that your branch is tracking the remote",
                            "# Visit your fork on GitHub to see the new branch"
                        ],
                        "tips": [
                            "This pushes your branch to your fork on GitHub",
                            "You can see the branch on GitHub after pushing",
                            "The branch will be available for creating a pull request",
                            "Make sure your commit messages are clear and descriptive",
                            "Push your branch, not directly to main"
                        ]
                    },
                    {
                        "title": "Create a Pull Request",
                        "content": "Now create a pull request (PR) to propose your changes to the original repository. Go to your fork on GitHub and click the 'Compare & pull request' button. Fill out the pull request template with a clear description of your changes, why they're needed, and any relevant information. Pull requests are the primary way to contribute to open source projects.",
                        "commands": [
                            "# Do this on GitHub website",
                            "# Click 'Compare & pull request' button on your branch",
                            "# Fill out the PR template with clear description",
                            "# Add screenshots or additional context if helpful"
                        ],
                        "tips": [
                            "Pull requests let others review your changes",
                            "Include a clear description of what you changed and why",
                            "Reference any related issues in your PR description",
                            "Add screenshots if your changes affect the UI",
                            "Be responsive to feedback from maintainers"
                        ]
                    },
                    {
                        "title": "Respond to Review Feedback",
                        "content": "After creating your pull request, maintainers may review your code and provide feedback. Be prepared to make additional changes based on their suggestions. This collaborative review process improves code quality and helps you learn from experienced developers. Address all review comments and update your pull request accordingly.",
                        "commands": [
                            "# Make additional changes based on feedback",
                            "git add .",
                            "git commit -m 'Address review feedback'",
                            "git push origin my-feature-branch  # Push the updates"
                        ],
                        "tips": [
                            "Be open to constructive feedback",
                            "Address all review comments thoroughly",
                            "Update your pull request description if needed",
                            "Thank reviewers for their time and suggestions",
                            "Learn from the feedback for future contributions"
                        ]
                    }
                ],
                "summary": "You learned the complete workflow for collaborating on GitHub projects, from finding a project to contribute to, forking repositories, making changes, and creating pull requests. This process enables you to contribute to open source projects and collaborate with developers worldwide. Remember that contributing to open source is not just about code - it's about being part of a community and helping projects grow.",
                "next_steps": [
                    "Learning about code reviews and best practices",
                    "Handling complex merge conflicts",
                    "Understanding different Git workflows (Git Flow, GitHub Flow)",
                    "Contributing to larger projects with more complex structures",
                    "Becoming a maintainer of open source projects",
                    "Exploring GitHub's advanced collaboration features"
                ]
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
