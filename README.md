# Keyboard and mouse automation based on PyAutoGUI and PySide6

## 1. `How to install`
```bash
#Upgrade pip
python -m pip install --upgrade pip

# Requirements
pip install PySide6
pip install pyautogui
pip install pyinstaller
```

## 2. `How to package python scripts`
```bash
pyinstaller --onefile --windowed --add-data "icon/gear.png;icon" --add-data "target.csv;." --hidden-import=pyautogui --hidden-import=PySide6.QtWidgets --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui .\pydirector.py
```


## 3. `How to Run`
> Run the executable in the `dist` folder directly and follow the instructions.

## 4. `About Compilation and Data Paths`

### a. If there is no `actions.db` in the `dist` folder

1. **Dynamic Creation**:
- The script creates `actions.db` at runtime using `create_database()`. It is not a pre-existing file that PyInstaller bundles into the `dist` folder (such as `target.csv` or `icon/gear.png`, which we explicitly add via `--add-data`).
- The `dist` folder only contains the compiled executable (`pydirector.exe`) and any files explicitly included via `--add-data`. Since we did not include `actions.db` using `--add-data` (and should not do so since it is dynamically generated), it will not appear there.

2. **Location defined by `DB_PATH`**:
- We use `DB_PATH = os.path.join(os.path.expanduser("~"), "actions.db")` to place the database in the user's home directory (e.g., `C:\Users\Lenovo\actions.db` on Windows). This is outside the `dist` folder, which is typically located in the project directory (e.g., `C:\path\to\your\project\dist`).

3. **PyInstaller `--onefile` behavior**:
- With `--onefile`, all bundled files (such as `target.csv` and `gear.png`) are extracted to a temporary directory (`sys._MEIPASS`) at runtime instead of the `dist` folder. However, `actions.db` is not bundled - it is created and written to the location specified by `DB_PATH`, which has nothing to do with the `dist` folder or temporary extraction.

---

### b. Where to find `actions.db`
Since `DB_PATH` is set to `os.path.join(os.path.expanduser("~"), "actions.db")`, the database file is stored in the **user's home directory**, not in the `dist` folder. Here's how to find it:

- **On Windows**:
- Path: `C:\Users\YourUsername\actions.db`
- Example: If the username is `Lenovo`, then find `C:\Users\Lenovo\actions.db`.
- How to check:
1. Open File Explorer.
2. Navigate to `C:\Users\Lenovo` (or press `Win + R`, type `%userprofile%`, and press Enter).
3. Find `actions.db`.

- **On macOS**:
-Path: `/Users/YourUsername/actions.db`
- Example: `/Users/lenovo/actions.db`
- How to check: Open Finder, press `Cmd + Shift + G`, enter `~`, and then look for `actions.db`.

- **On Linux**:
- Path: `/home/YourUsername/actions.db`
- Example: `/home/lenovo/actions.db`
- How to check: Open Terminal, enter `cd ~`, and then enter `ls -a` to view `actions.db`.

---

### c. Verify that it works
To confirm that the database is where it should be and contains data:
1. **Run the executable**:
- Execute `dist\pydirector.exe`.
- Add some actions (e.g., "Test Move", "move", "100,200") through the GUI.

2. **Check the file**:
- Navigate to your home directory (e.g., `C:\Users\Lenovo`).
- Look for `actions.db`. If data was written, it should exist and have a non-zero file size.

3. **Check the database**:
- Open `actions` using a SQLite viewer (e.g., DB Browser for SQLite) and verify that the `actions` table contains entries.
- Alternatively, add debug prints to your code:
  ```python
  def get_actions():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute('SELECT * FROM action ORDER BY id')
  action = cursor.fetchall()
  conn.close()
  print(f"Retrieved action from {DB_PATH}: {actions}") # Debug
  return action
  ```

4. **Check the log**:
-Open `pydirector.log` (in the same directory as the executable or wherever it is configured to write to) to see if the database actions were successfully logged.

### d. It is also possible to set it to save everything (including `actions.db`, ​​​​`target.csv`, and `icon/gear.png`) in the same folder as the executable (`pydirector.exe`).
This makes the application portable, meaning that the user can move the executable and its associated files to any directory and it will still work properly as long as the folder remains writable.

## 7. `Todo`

- Add `interruption` during running (CTRL-C doesn't seem to work)