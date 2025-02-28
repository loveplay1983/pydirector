# Keyboard and mouse automation based on PyAutoGUI and PySide6

### 1. How to install
```bash
# upgrade pip
python -m pip install --upgrade pip

# requirement
pip install PySide6
pip install pyautogui
pip install pyinstaller
```

### 2. How to package the python script
```
pyinstaller --onefile --windowed --add-data "icon/gear.png:icon" --hidden-import=pyautogui --hidden-import=other-pacakges filename.py
```

### 3. How to run
> Run the executable in the `dist` folder directly, and follow the instruction to arrange the actions. 

### 4. Todo
- Add `interruption` in the middle of running (CTRL-C seems taking no effect)
- 
