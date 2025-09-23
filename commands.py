from langchain.prompts import PromptTemplate
from utils import safe_json_parse, validate_json
import json

class CommandHelper:
    def __init__(self, llm):
        self.llm = llm
        self.temperature = 0.6
        self.max_tokens = 1200

        # 🔹 Prompt enforces JSON response
        self.command_prompt = PromptTemplate(
            input_variables=["command"],
            template="""You are an expert Git command syntax helper with deep knowledge of all Git commands and their variations.
Analyze the Git command: {command}

You MUST respond with a valid JSON object in the exact format specified below. Do not add any extra text or explanations outside the JSON.

Provide a detailed response in the following JSON format:
{{
    "syntax": "Complete command syntax with placeholders",
    "description": "What this command does, including its purpose and role in Git",
    "explanation": "Detailed explanation of how it works, including description and pro tips",
    "use_cases": [
        "Common use case 1 with brief explanation",
        "Common use case 2 with brief explanation",
        "Common use case 3 with brief explanation"
    ],
    "examples": [
        "Example command → Brief explanation of what it does",
        "Another example → Explanation",
        "Third example → Explanation"
    ],
    "important_flags": [
        {{"flag": "--flag", "description": "What this flag does and when to use it"}}
    ],
    "pitfalls": [
        "Common pitfall 1 and how to avoid it",
        "Common pitfall 2 and how to avoid it",
        "Common pitfall 3 and how to avoid it"
    ],
    "pro_tips": [
        "Pro tip 1 for better usage",
        "Pro tip 2 for efficiency",
        "Pro tip 3 for best practices"
    ],
    "related_commands": ["git command1", "git command2", "git command3"],
    "internal_mechanics": [
        "How Git handles this command internally (e.g., object creation, refs)",
        "Technical details about storage and operations"
    ]
}}

IMPORTANT INSTRUCTIONS:
- You must provide accurate information for ANY Git command, including subcommands, options, and variations.
- If the command is valid but not commonly used, still provide complete details.
- For complex commands, break down the explanation into clear, technical details.
- Always include at least 2-3 examples with practical scenarios.
- List all important flags and options, even if there are many.
- Provide specific pitfalls and pro tips based on real Git usage patterns.
- Include internal mechanics that explain how Git processes the command at the object level.
- Ensure the JSON is valid and contains ALL required fields.

⚠️ If the command is invalid or not recognized:
- Set "syntax" to "Invalid command"
- Add suggestions in "description" (e.g., use 'git help -a' or check spelling).

Make sure the JSON is valid and includes ALL fields. Provide comprehensive, accurate information for any Git command.

EXAMPLE RESPONSE FOR "git status":
{{
    "syntax": "git status [options]",
    "description": "Show the working tree status",
    "explanation": "Displays the state of the working directory and staging area, showing which files are staged, unstaged, or untracked.",
    "use_cases": [
        "Check what changes are ready to commit",
        "See which files are untracked",
        "Review the current branch and any differences"
    ],
    "examples": [
        "git status → Show status of all files",
        "git status --porcelain → Machine-readable output",
        "git status -s → Short format"
    ],
    "important_flags": [
        {{"flag": "--porcelain", "description": "Machine-readable output"}},
        {{"flag": "-s, --short", "description": "Short format"}},
        {{"flag": "--ignored", "description": "Show ignored files"}}
    ],
    "pitfalls": [
        "May show too much information in large repositories",
        "Does not show differences, only status"
    ],
    "pro_tips": [
        "Use 'git status -s' for quick overview",
        "Run before committing to ensure correct files are staged"
    ],
    "related_commands": ["git add", "git commit", "git diff"],
    "internal_mechanics": [
        "Reads the index and working directory",
        "Compares file hashes to determine status"
    ]
}}
"""
        )

        # Use LLM chain
        self.chain = self.command_prompt | self.llm

    def update_settings(self, temperature, max_tokens):
        """Update LLM settings dynamically"""
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm.temperature = temperature
        self.llm.max_tokens = max_tokens

    def get_command_help(self, command: str):
        """Get explanation for a Git command"""
        try:
            clean_command = command.strip().lower()

            # Run the chain
            response = self.chain.invoke({"command": clean_command})

            # Handle AIMessage or raw string
            if hasattr(response, "content"):
                response_content = response.content
            else:
                response_content = response

            # Try parsing JSON
            parsed_data = safe_json_parse(response_content)

            # Validate JSON structure
            if self._validate_command_data(parsed_data):
                return parsed_data
            else:
                return self._get_fallback_command_help(clean_command)

        except Exception as e:
            print(f"⚠️ Error: {e}")
            return self._get_fallback_command_help(command)

    def _validate_command_data(self, data):
        """Ensure JSON has all required fields"""
        required_fields = [
            "syntax", "description", "explanation",
            "use_cases", "examples", "important_flags",
            "pitfalls", "pro_tips", "related_commands",
            "internal_mechanics"
        ]
        return validate_json(data, required_fields)

    def _get_fallback_command_help(self, command):
        """Generic fallback for any command if LLM fails"""
        return {
            "syntax": "Unknown command",
            "description": f"'{command}' is not recognized",
            "explanation": "Try 'git help' for valid commands",
            "use_cases": [],
            "examples": [],
            "important_flags": [],
            "pitfalls": [],
            "pro_tips": [],
            "related_commands": ["git help", "git --help"],
            "internal_mechanics": []
        }


# ------------------ TEST ------------------
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()

    try:
        from langchain_groq import ChatGroq
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env")
        llm = ChatGroq(api_key=groq_api_key, model_name="llama-3.1-8b-instant", temperature=0.1)
        helper = CommandHelper(llm=llm)

        test_cmds = ["git commit", "git init", "git push", "git rebase", "git merge", "git status", "git log"]
        for cmd in test_cmds:
            print(f"\n--- {cmd} ---")
            data = helper.get_command_help(cmd)
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"⚠️ Cannot run test due to missing API key or dependencies: {e}")
        print("The CommandHelper class is ready for use with proper LLM setup.")
