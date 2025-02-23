import time
import logging
from typing import List
from langchain_ollama import OllamaLLM
from ai.models.schema import AgentResponse
from ai.config.AgentXSchema import AgentSchema, LlmConfig
from ai.config.AgentXProvider import getAgentSchema
import json
import re
from ollama import generate as ollama_generate
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
def create_openai_qa_model(agentSchema: AgentSchema):
    qa = AzureChatOpenAI(
        api_key=agentSchema.llmConfig.apiKey,
        azure_deployment=agentSchema.llmConfig.model,
        openai_api_version=agentSchema.llmConfig.apiVersion,  # type: ignore
        azure_endpoint=agentSchema.llmConfig.base_url,
        temperature=agentSchema.llmConfig.openAIConfig['temperature'],
    )
    return qa
 
def create_gpt4o(agentSchema: AgentSchema):
    qa = create_openai_qa_model(agentSchema)
    return qa
 
def extract_json(response: str):
    match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)
    return None

class Agent:
    def __init__(self, agentName: str = "qwen2.5-coder"):
        agentSchema: AgentSchema = getAgentSchema(agentName)
        self.name = agentSchema.name
        self.role = agentSchema.role
        self.agentSchema = agentSchema
        self.base_prompt = agentSchema.basePrompt
        self.useLangChain = agentSchema.useLangChain
        self.memory: List[str] = []
        self.llmConfig: LlmConfig = agentSchema.llmConfig

    def timed_generate(self, prompt: str, responseSchema = None, file_name: str = "response-llm") -> AgentResponse:
        start_time = time.time()
        logger.info(f"{self.name} agent generating content...")
        
        with open(f"contents/{self.name}-prompt.md", 'w', encoding='utf-8') as f:
            f.write(f"Prompt: {prompt}\n\n")

        response: AgentResponse = self.generate_structured(prompt, responseSchema) if responseSchema is not None else self.generate(prompt)
        
        with open(f"contents/{self.name}-{file_name}.md", 'w', encoding='utf-8') as f:
            f.write(response.content if responseSchema is None else json.dumps(response.content, indent=4))
        
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        logger.info(f"{self.name} agent generated content in {elapsed_time:.2f}ms.")
        
        return response

    def generate(self, prompt: str) -> AgentResponse:
        try:
            full_prompt = f"{self.base_prompt}\n\nRole: {self.role}\n\n{prompt}"
           
            if self.useLangChain:
                # Pass logic for connecting deployed LLM with LangChain here
                model = create_gpt4o(self.agentSchema)
                response = model(full_prompt)
                response = AgentResponse(content=response.content, metadata={"agent": self.name, "role": self.role, "json": True})
            else: 
                self.llm = OllamaLLM(
                    provider="openai",
                    model=self.llmConfig.model,
                    base_url=self.llmConfig.base_url,
                    temperature=self.llmConfig.openAIConfig['temperature']
                )

                content = self.llm.invoke(full_prompt)
                self.memory.append(content)
                response = AgentResponse(content=content, metadata={"agent": self.name, "role": self.role, "json": False})
            return response
            
        except Exception as error:
            logger.error(f"Error in {self.name} agent:", error)
            raise RuntimeError(f"{self.name} agent failed to generate content")

    def generate_structured(self, prompt: str, responseSchema = None) -> AgentResponse:
        """Generate content with structured response"""

        if self.useLangChain:
            # Pass logic for connecting deployed LLM with LangChain here
            model = create_gpt4o(self.agentSchema)
            # Get the format instructions
            promptTemplate = PromptTemplate(
                template=prompt
            )
            response = model(prompt)
            response = AgentResponse(content=extract_json(response.content), metadata={"agent": self.name, "role": self.role, "json": True})
        else:
            full_prompt = f"{self.base_prompt}\n\nRole: {self.role}\n\n{prompt}"
            response = ollama_generate(
                model=self.llmConfig.model,
                prompt=full_prompt,
                format=responseSchema,
                stream=False,
                options={
                    "temperature": self.llmConfig.openAIConfig['temperature']
                }
            )
            response = AgentResponse(content=json.loads(response.response), metadata={"agent": self.name, "role": self.role, "json": True})

        return response

    def update_safety_config(self, **kwargs):
        """Update safety configuration with new settings"""
        for key, value in kwargs.items():
            if hasattr(self.llmConfig.openAIConfig.config, key):
                setattr(self.llmConfig.openAIConfig.config, key, value)
            else:
                logger.warning(f"Unknown safety config parameter: {key}")

    def update_open_ai_config(self, **kwargs):
        """Update OpenAI configuration with new settings"""
        for key, value in kwargs.items():
            if hasattr(self.llmConfig.openAIConfig, key):
                setattr(self.llmConfig.openAIConfig, key, value)
            else:
                logger.warning(f"Unknown OpenAI config parameter: {key}")