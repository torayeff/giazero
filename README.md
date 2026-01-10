# GIA-0
Generally Intelligent Agent Zero

## Setup
```bash
conda create -n giazero python=3.12
conda activate giazero
pip install -r requirements.txt
cp env.example .env  # configure your API keys
```

## Usage
```bash
python giazero/agent.py --task-dir <TASK_DIR> --solution-dir <SOLUTION_DIR> [--model <MODEL>] [--user-prompt <PROMPT>]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--task-dir` | Yes | — | Path to task directory |
| `--solution-dir` | Yes | — | Path to output solutions |
| `--model` | No | `google_genai:gemini-3-flash-preview` | Model name |
| `--user-prompt` | No | `Solve the challenge.` | Initial prompt |

### Example
```bash
python giazero/agent.py \
    --task-dir tasks/hello-world \
    --solution-dir localdata/solutions/hello-world \
    --model google_genai:gemini-3-flash-preview \
    --user-prompt "Solve the challenge step by step."
```

## Extending Tools
Add custom tools in `giazero/tools.py` using the `@tool` decorator and append to the `tools` list:
```python
@tool
def my_tool(arg: str) -> str:
    """Tool description."""
    return result

tools = [..., my_tool]
```

## ⚠️ Warning
This agent has **full system access** with no guardrails. Use with caution.
