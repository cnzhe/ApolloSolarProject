from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.bot_config import AgentSystem

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced request model
class ChatRequest(BaseModel):
    message: str
    is_initial_greeting: bool = False  # Optional parameter with default value

# Initialize the agent system
agent_system = AgentSystem()

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # If it's an initial greeting, return a predefined response without invoking the agent system
        if request.is_initial_greeting:
            return {
                "summary": {
                    "text": "👋 Hello! I'm Soli, your solar energy assistant. How can I help you today?",
                    "quick_replies": [
                        "What solar incentives are available in my area?",
                        "How long do solar panels last?",
                        "What's the installation process like?"
                    ]
                },
                "details": {}
            }

        # Process user query through the agent system
        response = await agent_system.get_response(request.message)
        
        print(f"Request: {request.message}")
        print(f"Response: {response}")

        return response

    except Exception as e:
        # Enhanced error response matching the expected format
        return {
            "summary": {
                "text": f"An error occurred: {str(e)}",
                "quick_replies": [
                    "What solar incentives are available in my area?",
                    "How long do solar panels last?",
                    "What's the installation process like?"
                ]
            },
            "details": {}
        }

# For development server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
