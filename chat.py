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

        # Chat prompt - more universal Git/GitHub coverage
        self.chat_prompt = PromptTemplate(
            input_variables=["user_input", "chat_history"],
            template="""You are Gitguy, a comprehensive AI assistant specialized in all aspects of Git and GitHub.

            Chat History:
            {chat_history}

            User: {user_input}

            Provide a detailed, accurate, and helpful response about Git or GitHub. 
            You should universally answer any type of Git/GitHub-related question, including:
            - Basic commands and concepts
            - Advanced workflows and best practices
            - GitHub features, APIs, CI/CD, and integrations
            - Troubleshooting and error resolution
            - Common pitfalls and real-world tips

            If the user asks something unrelated to Git/GitHub, politely redirect them back to Git topics.

            Response guidelines:
            - Be friendly, encouraging, and patient, especially for beginners
            - Provide specific commands with explanations and examples
            - Explain concepts clearly with step-by-step instructions
            - Format commands as code blocks for easy copying
            - Include tips, common pitfalls, and best practices
            - Handle both basic and advanced Git/GitHub questions
            - If unsure, admit it and suggest reliable resources

            Response:"""
        )

        # Initialize memory for conversation history
        self.memory = ConversationBufferWindowMemory(
            k=5,
            memory_key="chat_history",
            return_messages=True
        )

        # Create chain using LangChain syntax
        self.chain = self.chat_prompt | self.llm

    def update_settings(self, temperature, max_tokens):
        """Update AI settings"""
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm.temperature = temperature
        self.llm.max_tokens = max_tokens

    def chat(self, user_input):
        """Chat with the user universally about Git/GitHub"""
        try:
            clean_input = user_input.strip()
            print(f"Debug: User input: {clean_input}")

            # Always let LLM handle response
            response = self.chain.invoke({"user_input": clean_input, "chat_history": ""})
            print(f"Debug: LLM response: {response}")

            return self._clean_response(response)

        except Exception as e:
            print(f"Error in chat: {e}")
            if "API key" in str(e) or "authentication" in str(e).lower():
                return "There seems to be an issue with the API key. Please check your .env file and ensure it's set correctly."
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                return "Network error occurred. Please check your internet connection and try again."
            else:
                return "I’m having trouble processing your question right now. Please try again."

    def _clean_response(self, response):
        """Clean up the AI response"""
        lines = response.content.strip().split('\n')
        clean_lines = [line.strip() for line in lines if line and not line.startswith(('Assistant:', 'AI:'))]
        return '\n'.join(clean_lines).strip()

    def get_chat_history(self):
        """Get the current chat history"""
        try:
            memory_vars = self.memory.load_memory_variables({})
            messages = memory_vars.get('chat_history', [])
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
