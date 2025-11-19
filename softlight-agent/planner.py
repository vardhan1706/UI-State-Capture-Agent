import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a UI navigation planner for a web automation agent.

Given a natural language task about using a web app (like "create a project in Linear"
or "filter a database in Notion"), output a clear, ordered list of atomic steps
for a browser automation script.

Rules:
- Each step should be a single UI action or observation.
- Refer to visible UI elements by their text labels where possible.
- Be generic: don't assume specific data in the user's account.
- Start from the given URL (the executor will open it first).
- Do NOT include code. Do NOT mention Playwright, Selenium, etc.
- Output ONLY a numbered list, like:
  1. ...
  2. ...
"""

def get_steps(task: str) -> list[str]:
    """
    Call the LLM to convert a natural language task into a list of UI steps.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.2,
    )

    content = response.choices[0].message.content
    lines = [line.strip() for line in content.splitlines() if line.strip()]

    steps: list[str] = []
    for line in lines:
        # Expect format like "1. Click on ..." or "2) Click ..."
        if line[0].isdigit():
            # Split on first dot or right parenthesis
            split_chars = [". ", ") "]
            step_text = line
            for ch in split_chars:
                if ch in line:
                    step_text = line.split(ch, 1)[1]
                    break
            steps.append(step_text.strip())
        else:
            # Fallback: treat as a step if we don't see numbers
            steps.append(line)

    return steps

if __name__ == "__main__":
    # Quick manual test
    demo_task = "How do I create a new project in Linear?"
    s = get_steps(demo_task)
    print("TASK:", demo_task)
    for i, step in enumerate(s, 1):
        print(f"{i}. {step}")
