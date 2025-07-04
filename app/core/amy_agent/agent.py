from google.adk.agents import Agent
from google.adk.memory import InMemoryMemoryService

amy_agent = Agent(
    name="Amy",
    # For live voice, you'll need a Gemini Live API model (e.g., "gemini-live-2.5-flash-preview-native-audio")
    # For now, we'll use a placeholder.
    model="gemini-2.5-flash",
    description="Your personal AI assistant, Amy, with persistent memory.",
    instruction="You are Amy, a helpful and friendly AI assistant. You remember past conversations.",
    
    tools=[] # No tools for now, we'll add them later
)

root_agent = amy_agent
