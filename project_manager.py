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


def generate_ai_project(brief, api_key, model="openai/gpt-oss-120b"):
    """
    Generate a project with Groq Structured Outputs.

    The model returns files as an array of {path, content} records instead
    of an object with arbitrary keys. Strict JSON Schema prevents malformed
    JSON (for example, broken quotes or Windows backslash escapes) from
    reaching the application.
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
        "additionalProperties": False,
    }

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "generated_project",
                "strict": True,
                "schema": schema,
            },
        },
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a software project generator. Return a complete small "
                    "educational project as structured data. Each file must be a "
                    "separate item with a relative path and complete text content. "
                    "Use real newlines inside file content. Do not put Markdown "
                    "fences around file contents. Do not use absolute paths, '..' "
                    "path segments, secrets, or destructive commands. Include a "
                    "README and a runnable entry point where appropriate."
                ),
            },
            {"role": "user", "content": brief},
        ],
    )

    raw = response.choices[0].message.content or ""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Groq returned a response that could not be parsed as JSON. "
            "Try again or choose another Groq model."
        ) from exc

    project_name = data.get("project_name")
    file_records = data.get("files")

    if not isinstance(project_name, str) or not project_name.strip():
        raise ValueError("Groq response did not include a valid project_name.")
    if not isinstance(file_records, list) or not file_records:
        raise ValueError("Groq response did not include a non-empty files array.")

    files = {}
    for record in file_records:
        if not isinstance(record, dict):
            raise ValueError("Groq returned an invalid file record.")
        relative_path = record.get("path")
        content = record.get("content")
        if not isinstance(relative_path, str) or not relative_path.strip():
            raise ValueError("Groq returned a file with an invalid path.")
        if not isinstance(content, str):
            raise ValueError(f"Groq returned invalid content for {relative_path!r}.")
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Groq returned an unsafe project path: {relative_path}")
        if relative_path in files:
            raise ValueError(f"Groq returned a duplicate file path: {relative_path}")
        files[relative_path] = content

    return {"project_name": project_name.strip(), "files": files}

