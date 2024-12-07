import autogen
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

BOT_CONFIG = {
    "config_list": [
        {
            "model": "llama3-8b-8192",
            "api_key": os.environ.get("GROQ_API_KEY"),
            "api_type": "groq",
        }
    ]
}

class AgentSystem:
    def __init__(self):
        self.config = BOT_CONFIG
        
        # Create the solar advisor agent
        self.solar_advisor = autogen.AssistantAgent(
            name="Solar_Advisor",
            llm_config=self.config,
            system_message="""You are a knowledgeable solar energy advisor. Help users understand solar energy concepts, the installation process, and guide them through the necessary steps for installation.
            - If you cannot provide a complete answer, still use 'FINAL ANSWER:' followed by the most helpful information you can offer
            - Be direct, concise, and provide actionable insights""",
        )
        
        # Create the financial expert agent
        self.financial_expert = autogen.AssistantAgent(
            name="Financial_Expert",
            llm_config=self.config,
            system_message="""You are a financial expert specializing in solar energy. Assist users in evaluating the costs, savings, and return on investment (ROI) for solar projects, as well as guiding them through incentives and financial options.""",
        )
        
        # Create the policy expert agent
        self.policy_expert = autogen.AssistantAgent(
            name="Policy_Expert",
            llm_config=self.config,
            system_message="""You are an expert in solar energy policies and incentives. Guide users through available government incentives, tax credits, and regulations that may affect their solar installation decisions.""",
        )
        
        # Create the user proxy agent (for automated interactions)
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",  # Disable manual human input
            max_consecutive_auto_reply=0,
            is_termination_msg=lambda x: isinstance(x, str) and "FINAL ANSWER:" in x.upper(),
        )
        
    async def get_response(self, user_message: str) -> str:
        try:
            # Reset chat messages to ensure a clean conversation
            if self.user_proxy.chat_messages:
                self.user_proxy.chat_messages.clear()

            # Initialize the chat with the user query
            self.user_proxy.initiate_chat(
                self.solar_advisor,
                message=f"""Process this user query: {user_message}
                If research is needed, collaborate with the financial expert and policy expert."""
            )

            # Give some time for the agents to process
            import asyncio
            await asyncio.sleep(2)

            # Retrieve chat history
            chat_history = self.user_proxy.chat_messages.get(self.solar_advisor, [])
            if not chat_history:
                return "No response from solar advisor."

            # Find the last message containing the final answer
            for message in reversed(chat_history):
                last_message = message.get("content", "")
                if "FINAL ANSWER:" in last_message.upper():
                    # Extract and return the final answer
                    response = last_message.split("FINAL ANSWER:")[-1].strip()
                    return response

            return "I don't know the answer to this yet."

        except Exception as e:
            return f"Error processing your request: {str(e)}"