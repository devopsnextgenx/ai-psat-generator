from dataclasses import dataclass
from .OpenAIConfig import OpenAIConfig
from typing import Optional

@dataclass
class LlmConfig:
    base_url: str
    model: str
    apiKey: Optional[str] = "DummyKey"
    apiVersion: Optional[str] = "2024-05-01-preview"
    openAIConfig: Optional[OpenAIConfig] = None

@dataclass
class AgentSchema:
    name: str
    role: str
    basePrompt: str
    llmConfig: LlmConfig
    isLogging: Optional[bool] = False
    useLangChain: Optional[bool] = False
