import os, queue, subprocess, threading, time, tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
import pyautogui
from pynput import keyboard
from project_manager import TEMPLATES, create_project, generate_ai_project
from typing_engine import type_text

class App:
 def __init__(self, root):
  self.root=root; root.title('VS Code Coding Automation Lab'); root.geometry('850x640')
  self.events=queue.Queue(); self.stop_event=threading.Event(); self.pause_event=threading.Event()
  self.worker=None; self.project=None
  self.folder=tk.StringVar(value=str(Path.home()/'CodingAutomationProjects'))
  self.name=tk.StringVar(value='coding_demo'); self.source=tk.StringVar(value='Built-in template')
  self.template=tk.StringVar(value=list(TEMPLATES)[0]); self.brief=tk.StringVar(value='Create a small Python project demonstrating a useful programming concept.')
  self.selected=tk.StringVar(); self.delay=tk.DoubleVar(value=.045); self.status=tk.StringVar(value='Ready')
  self.ui()
  self.listener=keyboard.Listener(on_press=self.hotkey); self.listener.daemon=True; self.listener.start()
  root.after(100,self.poll); root.protocol('WM_DELETE_WINDOW',self.close)
 def ui(self):
  f=ttk.Frame(self.root,padding=14); f.pack(fill='both',expand=True)
  ttk.Label(f,text='VS Code Coding Automation Lab',font=('Segoe UI',18,'bold')).pack(anchor='w')
  ttk.Label(f,text='Visible desktop-input testing tool.',foreground='#555').pack(anchor='w',pady=5)
  p=ttk.LabelFrame(f,text='Project setup',padding=9); p.pack(fill='x')
  r=ttk.Frame(p); r.pack(fill='x',pady=3)
  ttk.Label(r,text='Content source').pack(side='left')
  ttk.Combobox(r,textvariable=self.source,values=['Built-in template','AI-generated (OpenAI)'],state='readonly',width=22).pack(side='left',padx=5)
  ttk.Label(r,text='Template').pack(side='left')
  ttk.Combobox(r,textvariable=self.template,values=list(TEMPLATES),state='readonly',width=23).pack(side='left',padx=5)
  r=ttk.Frame(p); r.pack(fill='x',pady=3)
  ttk.Label(r,text='Project name').pack(side='left')
  ttk.Entry(r,textvariable=self.name,width=20).pack(side='left',padx=5)
  ttk.Entry(r,textvariable=self.folder).pack(side='left',fill='x',expand=True)
  ttk.Button(r,text='Browse',command=self.browse).pack(side='left',padx=4)
  r=ttk.Frame(p); r.pack(fill='x',pady=3)
  ttk.Entry(r,textvariable=self.brief).pack(side='left',fill='x',expand=True)
  ttk.Button(r,text='Create project',command=self.create).pack(side='left',padx=5)
  e=ttk.LabelFrame(f,text='VS Code input',padding=9); e.pack(fill='both',expand=True,pady=8)
  r=ttk.Frame(e); r.pack(fill='x')
  self.combo=ttk.Combobox(r,textvariable=self.selected,state='readonly',width=48); self.combo.pack(side='left')
  ttk.Button(r,text='Preview',command=self.preview).pack(side='left',padx=4)
  ttk.Button(r,text='Open in VS Code',command=self.open_editor).pack(side='left')
  self.text=tk.Text(e,font=('Consolas',10)); self.text.pack(fill='both',expand=True,pady=5)
  c=ttk.LabelFrame(f,text='Controls',padding=9); c.pack(fill='x')
  r=ttk.Frame(c); r.pack(fill='x')
  ttk.Label(r,text='Typing delay').pack(side='left')
  ttk.Scale(r,from_=.01,to=.2,variable=self.delay,length=180).pack(side='left',padx=6)
  ttk.Button(r,text='Start (5 sec)',command=self.start).pack(side='left',padx=3)
  ttk.Button(r,text='Pause / Resume (F6)',command=self.toggle).pack(side='left',padx=3)
  ttk.Button(r,text='Stop (F7)',command=self.stop).pack(side='left',padx=3)
  ttk.Label(r,textvariable=self.status).pack(side='right')
  ttk.Label(f,text='Open the file in VS Code, click inside the editor, then Start. F6 pauses/resumes; F7 stops. Move mouse to top-left corner for emergency stop.',foreground='#805000',wraplength=820).pack(anchor='w',pady=8)
 def browse(self):
  p=filedialog.askdirectory()
  if p:self.folder.set(p)
 def create(self):
  if self.source.get().startswith('Built-in'):
   try:self.set_project(create_project(self.folder.get(),self.name.get(),TEMPLATES[self.template.get()]))
   except Exception as e:messagebox.showerror('Error',str(e))
  else:
   key=os.getenv('OPENAI_API_KEY')
   if not key:messagebox.showerror('Missing key','Set OPENAI_API_KEY in PowerShell before launching.'); return
   self.status.set('Generating project...')
   threading.Thread(target=self.ai_create,args=(key,),daemon=True).start()
 def ai_create(self,key):
  try:
   data=generate_ai_project(self.brief.get(),key)
   self.events.put(('project',create_project(self.folder.get(),data.get('project_name',self.name.get()),data['files'])))
  except Exception as e:self.events.put(('error',str(e)))
 def set_project(self,path):
  self.project=Path(path); names=[str(p.relative_to(self.project)).replace('\\','/') for p in self.project.rglob('*') if p.is_file()]
  self.combo['values']=names; self.selected.set('main.py' if 'main.py' in names else names[0])
  self.preview(); self.status.set('Project ready')
  messagebox.showinfo('Project created',str(self.project))
 def preview(self):
  if not self.project or not self.selected.get():return
  self.text.delete('1.0','end'); self.text.insert('1.0',(self.project/self.selected.get()).read_text(encoding='utf-8'))
 def open_editor(self):
  if not self.project:
   messagebox.showwarning('No project selected', 'Create a project first.')
   return
  if not self.selected.get():
   messagebox.showwarning('No file selected', 'Select a file first.')
   return

  target = (self.project / self.selected.get()).resolve()
  if not target.is_file():
   messagebox.showerror('File not found', f'Could not find the selected file:\\n{target}')
   return

  # Locate the real Code.exe instead of launching the Windows code.cmd shim.
  candidates = [
   Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs' / 'Microsoft VS Code' / 'Code.exe',
   Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / 'Microsoft VS Code' / 'Code.exe',
   Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'Microsoft VS Code' / 'Code.exe',
  ]
  exe = next((p for p in candidates if p.is_file()), None)

  if exe is None:
   messagebox.showerror(
    'VS Code executable not found',
    'The code command works, but Code.exe was not found in the standard install locations.\\n'
    'Please locate Code.exe and share its full path.'
   )
   return

  try:
   subprocess.Popen(
    [str(exe), '--new-window', str(target)],
    cwd=str(self.project),
    close_fds=True
   )
   self.status.set(f'Opening {target.name} in VS Code...')
  except Exception as exc:
   messagebox.showerror('VS Code launch failed', f'{exc}\\n\\nFile: {target}')
 def start(self):
  if not self.project or not self.selected.get():messagebox.showwarning('Select file','Create a project first.'); return
  if self.worker and self.worker.is_alive():return
  text=(self.project/self.selected.get()).read_text(encoding='utf-8')
  self.stop_event.clear(); self.pause_event.clear()
  self.worker=threading.Thread(target=self.type_worker,args=(text,),daemon=True); self.worker.start()
  self.status.set('Switch to VS Code; 5-second countdown')
 def type_worker(self,text):
  try:
   for n in range(5,0,-1):
    if self.stop_event.is_set():return
    self.events.put(('status',f'Starting in {n}')); time.sleep(1)
   type_text(text,lambda:self.delay.get(),self.pause_event,self.stop_event)
   if not self.stop_event.is_set():self.events.put(('status','Typing completed'))
  except pyautogui.FailSafeException:self.events.put(('status','Emergency stop triggered'))
  except Exception as e:self.events.put(('error',str(e)))
 def toggle(self):
  if not self.worker or not self.worker.is_alive():return
  if self.pause_event.is_set():self.pause_event.clear(); self.status.set('Resumed')
  else:self.pause_event.set(); self.status.set('Paused')
 def stop(self):self.stop_event.set(); self.pause_event.clear(); self.status.set('Stop requested')
 def hotkey(self,key):
  if key==keyboard.Key.f6:self.events.put(('hotkey','toggle'))
  elif key==keyboard.Key.f7:self.events.put(('hotkey','stop'))
 def poll(self):
  try:
   while True:
    k,v=self.events.get_nowait()
    if k=='status':self.status.set(v)
    elif k=='project':self.set_project(v)
    elif k=='error':messagebox.showerror('Error',v)
    elif k=='hotkey':self.toggle() if v=='toggle' else self.stop()
  except queue.Empty:pass
  self.root.after(100,self.poll)
 def close(self):
  self.stop_event.set(); self.listener.stop(); self.root.destroy()

if __name__=='__main__':
 pyautogui.FAILSAFE=True
 root=tk.Tk()
 try:ttk.Style().theme_use('vista')
 except tk.TclError:pass
 App(root); root.mainloop()
