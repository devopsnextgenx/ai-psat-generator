from ai.config.AgentXSchema import LlmConfig, AgentSchema
from typing import List
import yaml
import os

agents = {}

def load_config(yaml_file_path: str = "./config/agentX.yml") -> List[AgentSchema]:
    with open(yaml_file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    for agent_data in config_data['agents']:
        if "openAIConfig" not in agent_data['llmConfig']:
            agent_data['llmConfig']['openAIConfig'] = None

        if "apiKey" not in agent_data['llmConfig']:
            agent_data['llmConfig']['apiKey'] = os.getenv("API_KEY")
        
        if "apiVersion" not in agent_data['llmConfig']:
            agent_data['llmConfig']['apiVersion'] = None

        llm_config = LlmConfig(
            base_url=agent_data['llmConfig']['base_url'],
            model=agent_data['llmConfig']['model'],
            apiKey=agent_data['llmConfig']['apiKey'],
            apiVersion=agent_data['llmConfig']['apiVersion'],
            openAIConfig=agent_data['llmConfig']['openAIConfig']
        )
        
        if "isLogging" not in agent_data:
            agent_data['isLogging'] = False

        if "useLangChain" not in agent_data:
            agent_data['useLangChain'] = False

        agent_schema = AgentSchema(
            name=agent_data['name'],
            role=agent_data['role'],
            basePrompt=agent_data['basePrompt'],
            isLogging=agent_data['isLogging'],
            useLangChain=agent_data['useLangChain'],
            llmConfig=llm_config
        )
        agents[agent_schema.name] = agent_schema
    
    return agents

def getAgents():
    if len(agents) == 0:
        load_config()
    return agents

def getAgentSchema(name: str) -> AgentSchema:
    return getAgents()[name]

# Example usage
if __name__ == "__main__":
    agents = getAgents()
    for agent in agents:
        print(agent)