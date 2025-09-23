import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import json
import json5
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
            raise ValueError("GROQ_API_KEY not found in environment variables")

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

    def _get_fallback_cheat_sheet(self):
        """Fallback cheat sheet when AI fails"""
        return {
            "basic_commands": [
                {"command": "git init", "description": "Initialize a new repository", "example": "git init"},
                {"command": "git add .", "description": "Stage all changes", "example": "git add ."},
                {"command": "git commit -m 'message'", "description": "Commit staged changes", "example": "git commit -m 'Initial commit'"},
                {"command": "git status", "description": "Show repository status", "example": "git status"},
                {"command": "git log", "description": "Show commit history", "example": "git log --oneline"}
            ],
            "branching": [
                {"command": "git branch", "description": "List branches", "example": "git branch"},
                {"command": "git branch <name>", "description": "Create new branch", "example": "git branch feature-branch"},
                {"command": "git checkout <branch>", "description": "Switch to branch", "example": "git checkout main"},
                {"command": "git merge <branch>", "description": "Merge branch into current", "example": "git merge feature-branch"}
            ],
            "remote_operations": [
                {"command": "git remote add origin <url>", "description": "Add remote repository", "example": "git remote add origin https://github.com/user/repo.git"},
                {"command": "git push -u origin <branch>", "description": "Push and set upstream", "example": "git push -u origin main"},
                {"command": "git pull", "description": "Fetch and merge from remote", "example": "git pull origin main"}
            ],
            "undo_operations": [
                {"command": "git reset --soft HEAD~1", "description": "Undo last commit (keep changes)", "example": "git reset --soft HEAD~1"},
                {"command": "git reset --hard HEAD~1", "description": "Undo last commit (discard changes)", "example": "git reset --hard HEAD~1"},
                {"command": "git revert <commit>", "description": "Create new commit that undoes changes", "example": "git revert abc123"}
            ],
            "merging": [
                {"command": "git merge <branch>", "description": "Merge branch into current", "example": "git merge feature-branch"},
                {"command": "git rebase <branch>", "description": "Rebase current branch onto another", "example": "git rebase main"}
            ]
        }
