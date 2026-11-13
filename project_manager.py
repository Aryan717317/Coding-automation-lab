from pathlib import Path
import re, time, json

TEMPLATES = {
 "Python CLI starter": {
  "README.md": "# Python CLI Starter\nRun: python main.py\n",
  "main.py": "def main():\n    tasks = []\n    while True:\n        task = input('Task (quit to exit): ').strip()\n        if task.lower() == 'quit':\n            break\n        if task:\n            tasks.append(task)\n            print(f'{len(tasks)} tasks saved')\n\nif __name__ == '__main__':\n    main()\n"
 },
 "FastAPI mini service": {
  "requirements.txt": "fastapi\nuvicorn[standard]\n",
  "main.py": "from fastapi import FastAPI\n\napp = FastAPI(title='Demo API')\n\n@app.get('/health')\ndef health():\n    return {'status': 'ok'}\n"
 }
}

def create_project(folder, name, files):
    root = Path(folder).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r'[^A-Za-z0-9_-]+', '_', name).strip('_') or 'project'
    target = root / safe
    if target.exists(): target = root / f'{safe}_{time.strftime("%Y%m%d_%H%M%S")}'
    target.mkdir()
    for rel, body in files.items():
        p = Path(rel)
        if p.is_absolute() or '..' in p.parts: raise ValueError('Unsafe project path')
        dest = target / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding='utf-8')
    return target

def generate_ai_project(brief, key):
    from openai import OpenAI
    client = OpenAI(api_key=key)
    result = client.chat.completions.create(
      model='gpt-4.1-mini', temperature=.2,
      messages=[
       {'role':'system','content':'Return only JSON: {"project_name":"name","files":{"relative/path":"complete file text"}}. Create a small safe educational project, 2-5 files. No destructive commands or paths outside project.'},
       {'role':'user','content':brief}
      ])
    raw = result.choices[0].message.content.strip()
    if raw.startswith('```'): raw = raw.split('\n',1)[1].rsplit('```',1)[0]
    data = json.loads(raw)
    if not isinstance(data.get('files'), dict) or not data['files']: raise ValueError('Invalid AI project response')
    return data
