from tools import tools

SYSTEM_PROMPT_TEMPLATE = """
You are an intelligent agent with exceptional coding skills. Solve the given task.

Task files: {task_dir}
Solution directory: {solution_dir}.
Write ALL files (solutions, scripts, intermediate files, etc.) ONLY to {solution_dir}.

Available tools:
{tools_description}
"""


def get_system_prompt(task_dir: str, solution_dir: str) -> str:
    """Generate system prompt with auto-populated tools list."""
    tools_description = "\n".join(
        f"- {t.name}: {t.description.split(chr(10))[0]}" for t in tools
    )
    return SYSTEM_PROMPT_TEMPLATE.format(
        task_dir=task_dir,
        solution_dir=solution_dir,
        tools_description=tools_description,
    )
