import os
#-----API KEYS IN .env DATEI SPEICHERN!-----
from dotenv import load_dotenv
load_dotenv()
#-------------------------------------------
from textwrap import dedent


from instructions_test import agent_instructions
from agno.agent import Agent
from agno.models.google import Gemini  # or Openai, Anthropic, etc.
from agno.tools.yfinance import YFinanceTools

gemini_api_key = os.getenv("GEMINI_API_KEY")

finance_agent = Agent(
    name='Finance Agent',
    model=Gemini(id='gemini-2.0-flash', api_key=gemini_api_key), 
    tools=[
        YFinanceTools(),
    ],
    instructions=agent_instructions,
    add_history_to_context=True,
    add_datetime_to_context=True,
    debug_mode=False,
    markdown=True,
)

user_input = input("Your question: ")
response = finance_agent.run(user_input)
print("\n" + response.content)
