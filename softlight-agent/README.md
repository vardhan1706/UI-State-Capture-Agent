# Softlight UI State Capture Agent

This project is a prototype agent that takes a natural-language task (e.g. “Create a new page in Notion”) and automatically:

1. Plans UI actions using an LLM  
2. Opens a real browser using Playwright  
3. Attempts the UI interactions  
4. Captures screenshots of each UI state  
5. Stores them in a structured dataset folder  

The goal is to demonstrate how an agent could guide another agent through a workflow inside any web application — including states that do not have unique URLs (such as modals, error banners, or fields updating).

---

## 🧠 How It Works

1. LLM Planner (`planner.py)

- Takes a natural-language task as input  
- Uses OpenAI API to produce a sequenced step-by-step plan  
- Has no app-specific logic — it works for Notion, Linear, or any other UI  
- Example:
  1. Open the Notion workspace homepage.
  2. Locate the sidebar.
  3. Click the "+ New page" button.

2. UI Executor (`executor.py`)

Uses Playwright to:

- Open the target website
- Attempt actions from the LLM plan (primarily text-based clicking)
- Hash the DOM after each step
- Capture a screenshot every step

Screenshot labeling:

- `ui_state_changed` → DOM changed after the step  
- `ui_state_same` → DOM did not change, but screenshot captured for traceability  

This allows the agent to detect intermediate UI states that do **not** update the URL.  
Many important UI states (modals, dropdowns, form fields, errors) are captured correctly.



3. CLI Interface (`main.py`)

You run:

python main.py

You provide:

- Task description  
- Base URL  

Example:

Create a new page in Notion
https://www.notion.so

The rest is automatic:
- Planner generates steps  
- Executor performs steps  
- Dataset folder is created with screenshots


📁 Dataset Structure

Each run generates a folder inside `dataset/`:

```
dataset/
  <task_slug>/
    00_initial_state_XXXX.png
    01_ui_state_changed_XXXX.png
    02_ui_state_same_XXXX.png
    ...
```

Example Task Folders Included

1. create_a_new_page_in_notion

The agent attempts to follow steps generated for Notion’s workspace.  
Because Notion requires authentication, interactions happen on the public interface.  
The system still captures:

- Page loads  
- DOM transitions  
- Element searches  
- UI state snapshots  

This demonstrates generalization despite authentication barriers.

---

2. create_a_database_in_notion

A second workflow on Notion that shows the planner and executor adapting to a different task with zero app-specific logic.  
Screenshots show multiple state captures as the agent processes the steps.

---

3. create_a_new_project_in_linear

Linear redirects into Google OAuth.  
Automated Playwright browsers are considered “insecure” by Google, so the login fails — but this produces a highly realistic UI sequence.

The agent captures:

- Linear landing page  
- Google sign-in form  
- Partially filled email field  
- “This browser or app may not be secure” error  
- Return to login screen  

This shows the agent handling:

- multi-step auth redirects  
- error states  
- DOM changes  
- unexpected UI flows  

while still fulfilling its core job: capture all UI states.

---

## 🛠️ Technology Stack

- Python
- Playwright (Chromium)
- OpenAI (LLM planning)
- dotenv
- SHA-256 DOM hashing

---

## 🎥 Loom Demo

A short Loom video demonstrating:

- Running the agent  
- Browser automation  
- Step-by-step UI state capture  
- Dataset visualization  

is included in the submission.

---

📌 Summary

This project demonstrates a generalizable architecture capable of:

- Understanding natural-language UI tasks  
- Planning action steps using an LLM  
- Navigating live web apps  
- Detecting non-URL UI transitions  
- Capturing screenshots of every UI state  
- Organizing datasets automatically  

The approach is app-agnostic and can be extended with:

- more action types (inputs, selects, form fills)  
- vision-based element targeting  
- planning-feedback loops  
- richer state extraction  

This satisfies the key requirements of the Softlight assignment.
