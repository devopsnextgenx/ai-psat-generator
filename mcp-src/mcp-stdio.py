import logging
from mcp.server.fastmcp import FastMCP
from random import random
import base64
import requests

logging.basicConfig(
    filename='/home/kira/mcp_server.log',
    filemode='a',  # append mode
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# Log startup information
logging.info("Starting MCP server")

# Initialize the server
server = FastMCP("mcp-calculator", log_level="ERROR")

# Define and register the function as a tool
@server.tool(name="calculateSum", description="Calculate the sum of two numbers")
def calculateSum(a, b):
    """Calculate the sum of two numbers
    
    Args:
        a (int): First number
        b (int): Second number

    Returns:
        int: Sum of a and b
    """
    logging.info(f"calculateSum function called with: {a}, {b}")
    return a + b

@server.tool(name="encryptBase64", description="Encrypt a message using base64")
def encryptBase64(message):
    """Encrypt a message using base64
    
    Args:
        message (str): Message to encrypt
        
    Returns:
        str: Encrypted message
    """
    logging.info(f"encryptBase64 function called with: {message}")
    return base64.b64encode(message.encode('utf-8')).decode('utf-8')

@server.tool(name="decryptBase64", description="Decrypt a message using base64")
def decryptBase64(message):
    """Decrypt a message using base64
    
    Args:
        message (str): Message to decrypt
        
    Returns:
        str: Decrypted message
    """
    logging.info(f"decryptBase64 function called with: {message}")
    return base64.b64decode(message).decode('utf-8')

@server.tool(name="echo", description="Echo a message back")
def echo(message):
    """Echo a message back
    
    Args:
        message (str): Message to echo
        
    Returns:
        str: The same message
    """
    logging.info(f"Echo function called with: {message}")
    
    return f"{message}: Random Number: {random()}"

@server.resource("resource://data/secret.txt")
def getSecret():
    """Get the secret message
    
    Returns:
        str: The secret message
    """
    with open("secret.txt", "r") as f:
        return f.read()

@server.resource(uri="resource://ollama/listModels", name="listModels", description="List all available models", mime_type="application/json")
async def listModels():
    """List all available models
    
    Returns:
        list: List of available models
    """
    # http://localhost:11434/api/tags
    url = "http://localhost:11434/api/tags"
    response = requests.get(url)
    return response.json()

@server.prompt(name="samplePrompt", description="Prompt the user for input")
async def samplePrompt(message):
    """Prompt the user for input
    
    Returns:
        str: User input
    """
    return "Enter a value: "+ message

if __name__ == "__main__":
    # Start the server
    server.run(transport="stdio")  # Based on the methods list, 'run' appears to be the correct method

