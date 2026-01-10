import argparse
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, TodoListMiddleware
from langchain.messages import HumanMessage
from system_prompt import get_system_prompt
from tools import tools

load_dotenv(override=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the agent to solve a task.")
    parser.add_argument(
        "--task-dir",
        type=Path,
        required=True,
        help="Path to the task directory containing the challenge files.",
    )
    parser.add_argument(
        "--solution-dir",
        type=Path,
        required=True,
        help="Path to the solution directory where outputs will be saved.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="google_genai:gemini-3-pro-preview",
        help="Model name to use (default: google_genai:gemini-3-pro-preview).",
    )
    parser.add_argument(
        "--user-prompt",
        type=str,
        default="Solve the challenge.",
        help="Initial user prompt to send to the agent (default: 'Solve the challenge.').",
    )
    args = parser.parse_args()

    task_dir = args.task_dir.resolve()
    solution_dir = args.solution_dir.resolve()

    system_prompt = get_system_prompt(task_dir=task_dir, solution_dir=solution_dir)

    agent = create_agent(
        model=args.model,
        tools=tools,
        system_prompt=system_prompt,
        middleware=[
            TodoListMiddleware(),
            SummarizationMiddleware(
                model=args.model,
                trigger=("fraction", 0.75),
                keep=("fraction", 0.25),
            ),
        ],
    )

    for event in agent.stream(
        {"messages": [HumanMessage(content=args.user_prompt)]},
        stream_mode="values",
    ):
        event["messages"][-1].pretty_print()
