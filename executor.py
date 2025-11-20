import time
import hashlib
import re
from uuid import uuid4
from pathlib import Path
from typing import List, Optional

from playwright.sync_api import sync_playwright, Page


def slugify(text: str) -> str:
    """
    Turn a task name into a folder-safe string.
    Example: "Create project in Linear" -> "create_project_in_linear"
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or f"task_{uuid4().hex[:8]}"


def get_dom_hash(page: Page) -> str:
    """
    Simple DOM-based state fingerprint using the page HTML.
    """
    html = page.content()
    return hashlib.sha256(html.encode("utf-8")).hexdigest()


def capture_state(
    page: Page,
    folder: Path,
    label: str,
    step_index: Optional[int] = None,
) -> str:
    """
    Capture a screenshot into the given folder with a structured filename.
    """
    folder.mkdir(parents=True, exist_ok=True)

    if step_index is not None:
        filename = f"{step_index:02d}_{label}_{uuid4().hex[:4]}.png"
    else:
        filename = f"{label}_{uuid4().hex[:4]}.png"

    out_path = folder / filename
    page.screenshot(path=str(out_path), full_page=True)
    print(f"[CAPTURE] Saved screenshot: {out_path}")
    return str(out_path)


def extract_click_target(step: str) -> Optional[str]:
    """
    Heuristic to extract a label we might click on from a step description.

    Examples:
    - 'Click the "New project" button in the left sidebar'
      -> 'New project'
    - 'Click on Settings in the sidebar'
      -> 'Settings'
    """
    # Prefer any text inside double quotes
    m = re.search(r'"([^"]+)"', step)
    if m:
        return m.group(1).strip()

    # Fallback: quick heuristic for last capitalized word/phrase
    words = step.split()
    candidates = [w for w in words if w and w[0].isupper()]
    if candidates:
        return " ".join(candidates[-1:])

    return None


def execute_steps(
    base_url: str,
    steps: List[str],
    task_name: str,
    headless: bool = False,
    wait_between_steps: float = 2.0,
) -> None:
    """
    Open the browser, navigate to the base_url, then iteratively execute
    each step in a generic way, capturing UI state for EVERY step.
    We still track DOM hash changes to label states as "changed" vs "same".
    """
    task_slug = slugify(task_name)
    output_folder = Path("dataset") / task_slug
    output_folder.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Output folder: {output_folder}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        print(f"[INFO] Navigating to {base_url}")
        page.goto(base_url, wait_until="load")
        time.sleep(2)

        # Initial state
        last_dom_hash = get_dom_hash(page)
        capture_state(page, output_folder, label="initial_state", step_index=0)

        for i, step in enumerate(steps, 1):
            print(f"\n[STEP {i}] {step}")

            step_lower = step.lower()

            # Very simple action handling:
            if "click" in step_lower:
                target_text = extract_click_target(step)
                if target_text:
                    print(f"[ACTION] Trying to click element with text: '{target_text}'")
                    try:
                        page.get_by_text(target_text, exact=False).first.click(timeout=5000)
                    except Exception as e:
                        print(f"[WARN] Failed to click by text '{target_text}': {e}")
                else:
                    print("[WARN] No obvious click target found in step description.")
            else:
                print("[ACTION] No direct action implemented for this step. Treating as observe/wait.")

            # Give the UI time to update
            time.sleep(wait_between_steps)

            # Always capture; label by whether DOM changed
            new_hash = get_dom_hash(page)
            if new_hash != last_dom_hash:
                print("[STATE] DOM changed – capturing new UI state.")
                label = "ui_state_changed"
            else:
                print("[STATE] DOM did not change – capturing anyway for traceability.")
                label = "ui_state_same"

            capture_state(page, output_folder, label=label, step_index=i)
            last_dom_hash = new_hash

        browser.close()
        print("\n[INFO] Browser closed.")
        print(f"[DONE] Screenshots for task '{task_name}' stored in: {output_folder}")
