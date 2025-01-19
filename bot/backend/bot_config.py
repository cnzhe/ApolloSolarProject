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
            max_consecutive_auto_reply=10,  # Allow more back-and-forth
            is_termination_msg=lambda x: isinstance(x, str) and "FINAL ANSWER:" in x.upper(),
        )
        
    async def get_response(self, user_message: str) -> str:
        try:
            # Reset chat messages to ensure a clean conversation
            if hasattr(self.user_proxy, 'chat_messages') and self.user_proxy.chat_messages:
                self.user_proxy.chat_messages.clear()

            # Create a group chat for collaboration
            groupchat = autogen.GroupChat(
                agents=[self.solar_advisor, self.financial_expert, self.policy_expert, self.user_proxy],
                messages=[],
                max_round=10
            )
            
            manager = autogen.GroupChatManager(groupchat=groupchat)

            # Initialize the chat with the user query
            await self.user_proxy.a_initiate_chat(
                manager,
                message=f"""Process this user query: {user_message}
                Collaborate to provide the most comprehensive answer."""
            )

            # Retrieve chat history
            chat_history = self.user_proxy.chat_messages.get(manager, [])
            if not chat_history:
                return "No response generated yet."

            # Find the last message containing the final answer
            for message in reversed(chat_history):
                last_message = message.get("content", "")
                if "FINAL ANSWER:" in last_message.upper():
                    # Extract and return the final answer
                    response = last_message.split("FINAL ANSWER:")[-1].strip()
                    return response

            # If no final answer is found, return the last message
            if chat_history:
                return chat_history[-1].get("content", "Still processing the request...")

            return "No response was generated."

        except Exception as e:
            return f"Error processing your request: {str(e)}"