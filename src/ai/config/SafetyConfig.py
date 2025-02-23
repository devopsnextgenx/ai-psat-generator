from typing import List
from dataclasses import dataclass

@dataclass
class SafetyConfig:
    allow_violence: bool = False
    allow_controversial_topics: bool = False
    sensitive_topics: List[str] = None
    
    def to_prompt_guidelines(self) -> str:
        guidelines = ["Please write content following these guidelines:"]
        
        if not self.allow_violence:
            guidelines.append("- Avoid violence topics")
            
        if not self.allow_controversial_topics:
            guidelines.append("- Avoid controversial topics")

        if self.sensitive_topics:
            topics = ", ".join(self.sensitive_topics)
            guidelines.append(f"- Avoid the following topics: {topics}")

        return "\n".join(guidelines)
