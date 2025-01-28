from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.bot_config import AgentSystem

# Create FastAPI app
app = FastAPI()

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Model for incoming messages
class ChatRequest(BaseModel):
    message: str

# Initialize the agent system
agent_system = AgentSystem()

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Get response from agent system
        response = await agent_system.get_response(request.message)
        print(f"Response: {response}")
        
        # Return the response as expected by the frontend
        return response
    except Exception as e:
        return {
            "text": f"An error occurred: {str(e)}",
            "sections": []
        }

# # For running the server
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)