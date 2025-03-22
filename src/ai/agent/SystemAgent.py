import logging
from ai.agent.Agent import Agent
from ai.models.schema import AgentResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemAgent:
    def __init__(self):
        self.agents = {
            "bot": Agent(
                agentName="qwen2.5-coder"
            )
        }

    def executeQuery(self, prompt: str) -> str:
        """Query the LLM with a prompt and return the response"""

        # print a physics question for friction, body, accelaration and force interation
        # list 5 questions on friction topic with different level of complexity and hardness, have couple of questions with true false 
        agentPrompt = f"""
            Answer based on the following prompt:
            {prompt}

            Keep response as you are a chatbot and answering in Female human voice.
        """

        action_response: AgentResponse  = self.agents['bot'].timed_generate(agentPrompt)

        return action_response