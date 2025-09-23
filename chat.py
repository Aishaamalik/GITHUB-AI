from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.runnables import RunnablePassthrough
from utils import safe_json_parse, validate_json
import json

class ChatAssistant:
    def __init__(self, llm):
        self.llm = llm
        self.temperature = 0.7
        self.max_tokens = 1000

        # Chat prompt
        self.chat_prompt = PromptTemplate(
            input_variables=["user_input", "chat_history"],
            template="""You are Gitguy, a helpful AI assistant for Git and GitHub questions.

            Chat History:
            {chat_history}

            User: {user_input}

            Provide a helpful, accurate response about Git or GitHub. If the question is not Git-related, politely redirect to Git topics.

            Response guidelines:
            - Be friendly and encouraging, especially for beginners
            - Provide specific commands when relevant
            - Explain concepts clearly with examples
            - If giving commands, format them as code blocks
            - Keep responses concise but comprehensive
            - If you don't know something, admit it and suggest alternatives

            Response:"""
        )

        # Initialize memory for conversation history
        self.memory = ConversationBufferWindowMemory(
            k=5,  # Keep last 5 exchanges
            memory_key="chat_history",
            return_messages=True
        )

        # Create chain using new LangChain syntax
        self.chain = self.chat_prompt | self.llm

    def update_settings(self, temperature, max_tokens):
        """Update AI settings"""
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm.temperature = temperature
        self.llm.max_tokens = max_tokens

    def chat(self, user_input):
        """Chat with the user about Git topics"""
        try:
            # Clean the input
            clean_input = user_input.strip()

            # Check if input is Git-related
            if not self._is_git_related(clean_input):
                return "I'm here to help with Git and GitHub questions! Could you ask me something about version control, repositories, or Git commands?"

            # Get response from AI
            response = self.chain.invoke({"user_input": clean_input})

            # Clean up response
            clean_response = self._clean_response(response)

            return clean_response

        except Exception as e:
            print(f"Error in chat: {e}")
            return "I apologize, but I'm having trouble processing your question right now. Please try again or ask about a specific Git command."

    def _is_git_related(self, user_input):
        """Check if the user input is related to Git/GitHub"""
        git_keywords = [
            'git', 'github', 'repository', 'repo', 'commit', 'branch', 'merge',
            'push', 'pull', 'clone', 'fork', 'pull request', 'pr', 'conflict',
            'rebase', 'reset', 'revert', 'stash', 'tag', 'remote', 'origin',
            'main', 'master', 'checkout', 'add', 'status', 'log', 'diff',
            'blame', 'bisect', 'cherry-pick', 'submodule', 'workflow', 'ci/cd'
        ]

        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in git_keywords)

    def _clean_response(self, response):
        """Clean up the AI response"""
        # Remove any unwanted prefixes or formatting
        lines = response.strip().split('\n')
        clean_lines = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith('Assistant:') and not line.startswith('AI:'):
                clean_lines.append(line)

        return '\n'.join(clean_lines).strip()

    def get_chat_history(self):
        """Get the current chat history"""
        try:
            # Get memory variables
            memory_vars = self.memory.load_memory_variables({})
            messages = memory_vars.get('chat_history', [])

            # Format messages for display
            formatted_history = []
            for msg in messages:
                if hasattr(msg, 'type') and msg.type == 'human':
                    formatted_history.append({"role": "user", "content": msg.content})
                elif hasattr(msg, 'type') and msg.type == 'ai':
                    formatted_history.append({"role": "assistant", "content": msg.content})

            return formatted_history

        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []

    def clear_history(self):
        """Clear the chat history"""
        try:
            self.memory.clear()
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False

    def get_memory_stats(self):
        """Get memory usage statistics"""
        try:
            memory_vars = self.memory.load_memory_variables({})
            messages = memory_vars.get('chat_history', [])
            return {
                "total_messages": len(messages),
                "memory_size": len(str(messages))
            }
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {"total_messages": 0, "memory_size": 0}
