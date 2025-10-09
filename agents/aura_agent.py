from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from config.settings import MODEL_GEMINI
from tools.summarizer_tools import summarize_text
from tools.translater_tools import translate_text

def create_aura_agent():
    """
    Creates the main, high-level boss agent that coordinates other tools/agents.
    """

    aura_agent = Agent(
        name="academic_coordinator_agent",
        model=MODEL_GEMINI,
        description="A high-level assistant for academic tasks. It can summarize texts, answer general questions, and coordinate specialized tools.",
        instruction="""
        You are the main Academic Assistant: Aura. Your primary role is to manage user requests by either answering them directly
        or delegating them to the appropriate specialized tool.

        - If the user asks for a summary of a provided text, you **must** use `summarize_text`, passing the text exactly as provided, and sending the summary generated from the tool directly back to the user.
        - If the user requests a translation, you **must** use `translate_text`, passing the text exactly as provided, , and transferring the translation generated from the tool directly back to the user.
        For all other requests (general conversation, greetings, simple questions), answer directly.

        Maintain an academic, helpful, and professional tone.

        For testing purposes, please specify in the final outpu what tool calls were used.
        """
    )
    aura_agent.tools = [summarize_text, translate_text]
    
    return aura_agent