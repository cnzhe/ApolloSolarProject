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
            system_message="""You are a solar energy advisor. Analyze the technical aspects and provide:
            1. Technical insights specific to user's context (2-3 sentences)
            2. Key technical recommendations (2-3 bullet points)
            Format your response as:
            TECHNICAL INSIGHTS: <assessment>
            RECOMMENDATIONS:
            • <recommendation 1>
            • <recommendation 2>""",
        )
        
        # Create the financial expert agent
        self.financial_expert = autogen.AssistantAgent(
            name="Financial_Expert",
            llm_config=self.config,
            system_message="""You are a solar energy financial strategist. Provide:
            1. Financial opportunities unique to user's context (2-3 sentences)
            2. Key financial recommendations (2-3 bullet points)
            Format your response as:
            FINANCIAL ANALYSIS: <analysis>
            NEXT STEPS:
            • <step 1>
            • <step 2>""",
        )
        
        # Create the policy expert agent
        self.policy_expert = autogen.AssistantAgent(
            name="Policy_Expert",
            llm_config=self.config,
            system_message="""You are a solar policy navigator. Provide:
            1. Policy insights that complement technical and financial advice (2-3 sentences)
            2. Available incentives for user's specific scenario (2-3 bullet points)
            Format your response as:
            POLICY OVERVIEW: <overview>
            AVAILABLE INCENTIVES:
            • <incentive 1>
            • <incentive 2>""",
        )
        
        # Create the coordinator agent to synthesize responses
        self.coordinator = autogen.AssistantAgent(
            name="Coordinator",
            llm_config=self.config,
            system_message="""You are a solar solutions coordinator. Your role is to:
            1. Review insights from all experts
            2. Create a brief executive summary (2-3 sentences)
            3. Highlight the most critical action items
            Format the final response as:
            SUMMARY: <executive summary>
            PRIORITY ACTIONS:
            • <action 1>
            • <action 2>""",
        )
        
        # Create the user proxy agent
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=5,
            is_termination_msg=lambda x: isinstance(x, str) and "PRIORITY ACTIONS:" in x,
        )

    async def get_response(self, user_message: str) -> Dict[str, Any]:
        try:
            # Reset chat history
            if hasattr(self.user_proxy, 'chat_messages'):
                self.user_proxy.chat_messages.clear()

            # Create group chat
            groupchat = autogen.GroupChat(
                agents=[
                    self.solar_advisor,
                    self.financial_expert,
                    self.policy_expert,
                    self.coordinator,
                    self.user_proxy
                ],
                messages=[],
                max_round=6
            )
            
            manager = autogen.GroupChatManager(groupchat=groupchat)

            # Start the chat
            await self.user_proxy.a_initiate_chat(
                manager,
                message=f"""Query: {user_message}
                Solar Advisor, Financial Expert, and Policy Expert, please provide your analyses.
                Coordinator, once all experts have shared insights, synthesize a final response."""
            )

            # Get chat history
            chat_history = self.user_proxy.chat_messages.get(manager, [])
            if not chat_history:
                return {
                    "summary": "No response generated.",
                    "details": {}
                }

            # Process the responses
            expert_insights = {
                "technical": {},
                "financial": {},
                "policy": {}
            }
            
            final_summary = ""
            priority_actions = []

            for message in chat_history:
                content = message.get("content", "")
                
                # Extract expert insights
                if "TECHNICAL INSIGHTS:" in content:
                    expert_insights["technical"]["assessment"] = content.split("TECHNICAL INSIGHTS:")[1].split("RECOMMENDATIONS:")[0].strip()
                    expert_insights["technical"]["recommendations"] = [
                        rec.strip() for rec in content.split("RECOMMENDATIONS:")[1].strip().split("•") if rec.strip()
                    ]
                elif "FINANCIAL ANALYSIS:" in content:
                    expert_insights["financial"]["analysis"] = content.split("FINANCIAL ANALYSIS:")[1].split("NEXT STEPS:")[0].strip()
                    expert_insights["financial"]["steps"] = [
                        step.strip() for step in content.split("NEXT STEPS:")[1].strip().split("•") if step.strip()
                    ]
                elif "POLICY OVERVIEW:" in content:
                    expert_insights["policy"]["overview"] = content.split("POLICY OVERVIEW:")[1].split("AVAILABLE INCENTIVES:")[0].strip()
                    expert_insights["policy"]["incentives"] = [
                        inc.strip() for inc in content.split("AVAILABLE INCENTIVES:")[1].strip().split("•") if inc.strip()
                    ]
                elif "SUMMARY:" in content:
                    final_summary = content.split("SUMMARY:")[1].split("PRIORITY ACTIONS:")[0].strip()
                    priority_actions = [
                        action.strip() for action in content.split("PRIORITY ACTIONS:")[1].strip().split("•") if action.strip()
                    ]

            final_summary = final_summary.replace("**", "").strip()
            priority_actions = [action.replace("**", "").strip() for action in priority_actions]

            return {
                "summary": {
                    "text": final_summary,
                    "actions": priority_actions
                },
                "details": expert_insights
            }

        except Exception as e:
            return {
                "summary": f"An error occurred: {str(e)}",
                "details": {}
            }