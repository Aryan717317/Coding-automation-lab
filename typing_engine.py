import time, random, pyautogui

def type_text(text, delay, pause, stop):
    for ch in text:
        if stop.is_set(): return
        while pause.is_set() and not stop.is_set(): time.sleep(.08)
        if stop.is_set(): return
        if ch == "\n": pyautogui.press("enter")
        elif ch == "\t": pyautogui.press("tab")
        else: pyautogui.write(ch)
        time.sleep(max(.005, delay()) * random.uniform(.8, 1.25))
