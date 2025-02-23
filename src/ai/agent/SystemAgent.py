import logging
from ai.agent.Agent import Agent
from ai.config.AgentXSchema import LlmConfig
from ai.models.schema import AgentResponse
from ai.operators.executer import ALLOWED_COMMANDS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_CHOICES = ['a', 'b', 'c', 'd']

class SystemAgent:
    def __init__(self):
        self.agents = {
            "bot": Agent(
                agentName="qwen2.5-coder"
            )
        }

    def executeQuery(self, prompt: str) -> str:
        """Query the LLM with a prompt and return the response"""

        responseSchema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string"
                    },
                    "answer": {
                            "type": "object",
                            "properties": {
                                "key": {
                                    "type": "string",
                                    "enum": ALLOWED_CHOICES
                                },
                                "explaination": {
                                    "type": "string"
                                }
                            },
                            "required": ["key", "explaination"]
                        },
                    "choices": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {
                                    "type": "string",
                                    "enum": ALLOWED_CHOICES
                                },
                                "value": {
                                    "type": "string"
                                }
                            },
                            "required": ["key", "value"]
                        },
                        "minItems": 2,
                        "maxItems": 4
                    }
                },
                "required": ["question", "answer", "choices"]
            },
            "minItems": 1
        }

        # print a physics question for friction, body, accelaration and force interation
        agentPrompt = f"""
            Build a multiple choice questions based on the following prompt:
            {prompt}

            Create exact number of questions based on the prompt.
            Make sure question is formatted in multiline markdown format, with numbers and key data elements as code.

            Provide the question, correct answer, and choices in the JSON format.
            {responseSchema}
        """

        action_response: AgentResponse  = self.agents['bot'].timed_generate(agentPrompt, "action_response")
        print(action_response)

        return action_response