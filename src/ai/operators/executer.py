import subprocess

ALLOWED_COMMANDS = ["ls", "du", "df", "whoami", "pwd", "echo", "curl", "mspaint"]

def execute_shell_command(command, args):

    agentCmd = [command] if len(args) == 0 else [command, *args]
    print(f"Executing command: {agentCmd}")
    
    try:
        result = subprocess.run(
            agentCmd, shell=False, text=True, capture_output=True
        )
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except Exception as e:
        return {"error": str(e)}

def process_command(llm_output):
    if llm_output.get("action") == "run_shell_command":
        command = llm_output.get("command")
        args = llm_output.get("args") if llm_output.get("args") else ''
        if validate_command(command):
            return execute_shell_command(command, args)
        else:
            return {"error": "Command not allowed"}
    return {"error": "Unsupported action"}

def validate_command(command):
    
    command_name = command.split()[0]
    return command_name in ALLOWED_COMMANDS

