# VS Code Coding Automation Lab

A Windows desktop application for transparent VS Code keyboard-input and UI automation testing.

## Features

- Create projects from built-in Python CLI and FastAPI templates.
- Optionally generate small projects through the OpenAI API.
- Preview generated files and open the selected file in VS Code.
- Send keyboard input to the focused editor for UI testing.
- Pause/resume with **F6** and stop with **F7**.
- PyAutoGUI corner fail-safe for emergency abort.

## Requirements

- Windows 10/11
- Python 3.10+
- Visual Studio Code

## Installation

1. Extract or clone this repository.
2. Double-click `run.bat`. It creates a virtual environment, installs dependencies, and launches the app.

Manual PowerShell setup:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## Usage

1. Choose **Built-in template** or **AI-generated (OpenAI)**.
2. Enter a project name and output folder, then select **Create project**.
3. Choose a file from the dropdown and select **Preview**.
4. Select **Open in VS Code**.
5. Focus the intended editor and return to the app.
6. Select **Start**. A five-second countdown gives you time to focus the editor.
7. Press **F6** to pause/resume or **F7** to stop. Move the mouse to the top-left screen corner for PyAutoGUI's emergency fail-safe.
8. Save the file in VS Code with Ctrl+S.

## Optional AI project generation

Set an OpenAI API key in PowerShell before launching:

```powershell
$env:OPENAI_API_KEY="your-api-key"
python main.py
```

Choose **AI-generated (OpenAI)** and enter a short project brief. The generator uses `gpt-4.1-mini`; API usage may incur charges. The key is read from the environment and is not saved in this repository.

## Safety and limitations

The application sends input to whichever window currently has focus. Verify the intended editor is focused before starting. Variable timing is intended for UI/input testing, not to claim a person is present or misrepresent automated activity.

The VS Code launcher checks common Windows installation locations for `Code.exe`. If VS Code is installed in a custom location, add that location to the candidate list in `main.py`.

## Project files

- `main.py` — Tkinter interface, project workflow, VS Code launcher, controls
- `typing_engine.py` — keyboard input simulation
- `project_manager.py` — built-in templates and optional AI project generation
- `requirements.txt` — Python dependencies
- `run.bat` — Windows setup and launcher
- `.gitignore` — excludes virtual environments, caches, logs, and secrets
