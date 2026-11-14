from pathlib import Path
import json
import re
import time


TEMPLATES = {
    "Python CLI starter": {
        "README.md": "# Python CLI Starter\nRun: python main.py\n",
        "main.py": (
            "def main():\n"
            "    tasks = []\n"
            "    while True:\n"
            "        task = input('Task (quit to exit): ').strip()\n"
            "        if task.lower() == 'quit':\n"
            "            break\n"
            "        if task:\n"
            "            tasks.append(task)\n"
            "            print(f'{len(tasks)} tasks saved')\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
        ),
    },
    "FastAPI mini service": {
        "requirements.txt": "fastapi\nuvicorn[standard]\n",
        "main.py": (
            "from fastapi import FastAPI\n"
            "\n"
            "app = FastAPI(title='Demo API')\n"
            "\n"
            "@app.get('/health')\n"
            "def health():\n"
            "    return {'status': 'ok'}\n"
        ),
    },
}


def create_project(folder, name, files):
    root = Path(folder).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "project"
    target = root / safe_name
    if target.exists():
        target = root / f"{safe_name}_{time.strftime('%Y%m%d_%H%M%S')}"
    target.mkdir(parents=True, exist_ok=False)

    for relative_path, body in files.items():
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Unsafe project path: {relative_path}")
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(str(body), encoding="utf-8")

    return target


def generate_ai_project(
    brief,
    api_key,
    model="openai/gpt-oss-120b",
    max_completion_tokens=32768,
):
    """
    Generate a project using Groq Structured Outputs.

    Uses a larger completion budget and low reasoning effort so code-heavy
    project generation is less likely to stop before the JSON document closes.
    """
    try:
        from groq import Groq
    except ImportError as exc:
        raise RuntimeError(
            "Groq SDK is not installed. Run: python -m pip install -r requirements.txt"
        ) from exc

    schema = {
        "type": "object",
        "properties": {
            "project_name": {"type": "string"},
            "files": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["project_name", "files"],
