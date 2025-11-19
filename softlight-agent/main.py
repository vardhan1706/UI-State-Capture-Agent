from planner import get_steps
from executor import execute_steps


def run_task_interactive():
    """
    Simple CLI: ask the user for a task and base URL, then run the agent.
    """
    print("=== Softlight UI State Capture Agent (Prototype) ===\n")

    task = input("Describe the task (e.g., 'Create a new project in Linear'): ").strip()
    base_url = input("Base URL to start from (e.g., 'https://linear.app'): ").strip()

    if not task or not base_url:
        print("Task and base URL are required. Exiting.")
        return

    print("\n[PLANNER] Generating steps from LLM...")
    steps = get_steps(task)
    print("\n[PLANNER] Steps:")
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")

    # You could ask: "Proceed? (y/n)" here if you want
    print("\n[EXECUTOR] Starting browser automation and state capture...")
    execute_steps(base_url=base_url, steps=steps, task_name=task, headless=False)


if __name__ == "__main__":
    run_task_interactive()
