import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools
from instructions import agent_instructions

# Load .env from parent directory (stock_m8/.env)
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=dotenv_path)

# Initialize FastAPI app
app = FastAPI()

# Get Gemini API key from environment
gemini_api_key = os.getenv("GEMINI_API_KEY")

class Query(BaseModel):
    prompt: str

# Initialize finance agent with Gemini model and YFinance tools
finance_agent = Agent(
    name='Finance Agent',
    model=Gemini(id='gemini-2.0-flash', api_key=gemini_api_key), 
    tools=[
        YFinanceTools(),
    ],
    instructions=agent_instructions,
    add_history_to_context=False,  # No database configured
    add_datetime_to_context=True,
    debug_mode=False,
    markdown=True,
)

@app.post("/ask")
def ask_agent(query: Query):
    """Process user query and return agent response."""
    response = finance_agent.run(query.prompt)
    return {"response": response.content}

# Local testing - uncomment to test directly
if __name__ == "__main__":
    print("🚀 Finance Agent - Local Test Mode\n")
    
    # Test with a sample query
    test_query = input("Enter stock ticker or question (e.g., 'AAPL'): ")
    
    print("\n⏳ Processing...\n")
    response = finance_agent.run(test_query)
    
    print("="*60)
    print(response.content)
    print("="*60)
