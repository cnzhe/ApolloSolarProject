import autogen
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent
import re

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
        
        # User Proxy Agent - Entry and Final Check
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=None,
            is_termination_msg=lambda x: isinstance(x, str) and "NEXT STEPS:" in x,
        )
        
        # Context Retrieval Agent (Parallel Processing)
        self.retrieval_agent = autogen.AssistantAgent(
            name="Retrieval_Agent",
            llm_config=self.config,
            system_message="""Retrieve past user interactions and relevant history asynchronously.
            Scope: Only fetch information related to solar energy installations, incentives, and financing.""",
        )
        
        # User Context Agent
        self.user_context_agent = autogen.AssistantAgent(
            name="User_Context_Agent",
            llm_config=self.config,
            system_message="""Extract key information needs and context from user messages.
            Ensure that validated insights are forwarded for aggregation instead of just confirming correctness.""",
        )
        
        # Follow-Up Agent
        self.follow_up_agent = autogen.AssistantAgent(
            name="Follow_Up_Agent",
            llm_config=self.config,
            system_message="""Review the conversation and suggest 2-3 short follow-up questions that the user might want to explore next.
            - These questions should be related to the current conversation context.
            - Structure the response in this format:
            SUGGESTED QUESTIONS:
            [1] Question 1
            [2] Question 2
            [3] Question 3""",
        )
        
        # Analysis Agent - Ensures full response aggregation and conciseness
        self.analysis_agent = autogen.AssistantAgent(
            name="Analysis_Agent",
            llm_config=self.config,
            system_message="""Review the conversation and come up with an insightful final response.
            - The final response must directly answer the user's query.
            - Exclude information that is not directly related to the user's query.
            - **No meta-comments or unnecessary explanations**—keep it focused.
            - Structure the response in a readable way, start with FINAL ANSWER: [answer]""",
        )

    
    async def get_response(self, user_message: str) -> Dict[str, Any]:
        try:
            if hasattr(self.user_proxy, 'chat_messages'):
                self.user_proxy.chat_messages.clear()
            
            # Create pipeline chat
            groupchat = autogen.GroupChat(
                agents=[
                    self.user_proxy,
                    # self.user_context_agent,
                    self.retrieval_agent,
                    self.analysis_agent,
                    self.follow_up_agent,
                ],
                messages=[],
                speaker_selection_method="auto",
                max_round=5
            )
            
            manager = autogen.GroupChatManager(groupchat=groupchat)
            society_of_mind_agent = SocietyOfMindAgent(
                "society_of_mind",
                chat_manager=manager,
            )
            
            await self.user_proxy.a_initiate_chat(
                society_of_mind_agent,
                message=f"""User Query: {user_message}
                Process query dynamically through retrieval, validation, and analysis."""
            )
            
            chat_history = self.user_proxy.chat_messages.get(manager, [])
            final_message = chat_history[-2].get("content", "") if chat_history else "I couldn't process your request."
            follow_up_questions = chat_history[-1].get("content", "") if chat_history else []
            
            if 'SUGGESTED QUESTIONS:' in follow_up_questions:
                # Extract everything after 'SUGGESTED QUESTIONS:'
                suggested_section = follow_up_questions.split('SUGGESTED QUESTIONS:')[1].strip()
                suggested_questions = re.findall(r'\[\d+\] (.+)', suggested_section)
            else:
                # Default fallback questions
                suggested_questions = [
                    "Tell me more about financing options",
                    "What's the next step in the process?",
                    "How long does it take to install solar panels?"
                ]

            print(final_message, suggested_questions)
            
            return {
                "summary": {
                    "text": final_message.split('FINAL ANSWER:')[1],
                    "quick_replies": suggested_questions
                },
                "details": {}
            }
        
        except Exception as e:
            return {
                "summary": {
                    "text": f"An error occurred: {str(e)}",
                    "quick_replies": [
                        "What solar incentives are available?",
                        "How much could I save with solar?",
                        "Tell me about installation"
                    ]
                },
                "details": {}
            }
