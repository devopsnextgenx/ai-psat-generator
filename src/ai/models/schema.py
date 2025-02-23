import logging
from typing import Optional, Dict, Union, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    content: Optional[Union[str, Dict[str, Any]]] = None
    metadata: Optional[Dict] = None