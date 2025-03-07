# Keyboard and mouse automation based on PyAutoGUI and PySide6

## 1.`How to install`
```bash
# upgrade pip
python -m pip install --upgrade pip

# requirement
pip install PySide6
pip install pyautogui
pip install pyinstaller
```

## 2. `How to package the python script`
```bash
pyinstaller --onefile --windowed --add-data "icon/gear.png;icon" --add-data "target.csv;." --hidden-import=pyautogui --hidden-import=PySide6.QtWidgets --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui .\pydirector.py
```
[text](target.csv) [text](icon) [text](actions.db)

## 3. `How to run`
> Run the executable in the `dist` folder directly, and follow the instruction to arrange the actions. 

## 4. `About compiling and data path`


### a. If `actions.db` is not in the `dist` Folder
1. **Dynamic Creation**:
   - The script creates `actions.db` at runtime using `create_database()`. It’s not a pre-existing file that PyInstaller bundles into the `dist` folder (like `target.csv` or `icon/gear.png`, which we explicitly added with `--add-data`).
   - The `dist` folder only contains the compiled executable (`pydirector.exe`) and any files explicitly included via `--add-data`. Since we didn’t include `actions.db` with `--add-data` (and shouldn’t, as it’s generated dynamically), it won’t appear there.

2. **Location Defined by `DB_PATH`**:
   - We use `DB_PATH = os.path.join(os.path.expanduser("~"), "actions.db")`, which places the database in the user’s home directory (e.g., `C:\Users\Lenovo\actions.db` on Windows). This is outside the `dist` folder, which is typically located in the project directory (e.g., `C:\path\to\your\project\dist`).

3. **PyInstaller `--onefile` Behavior**:
   - With `--onefile`, all bundled files (like `target.csv` and `gear.png`) are extracted to a temporary directory (`sys._MEIPASS`) at runtime, not the `dist` folder. However, `actions.db` isn’t bundled—it’s created and written to the location specified by `DB_PATH`, which is independent of the `dist` folder or temporary extraction.

---

### b. Where to Find `actions.db`
Since `DB_PATH` is set to `os.path.join(os.path.expanduser("~"), "actions.db")`, the database file is stored in the **user’s home directory**, not the `dist` folder. Here’s how to locate it:

- **On Windows**:
  - Path: `C:\Users\YourUsername\actions.db`
  - Example: If the username is `Lenovo`, look in `C:\Users\Lenovo\actions.db`.
  - How to check:
    1. Open File Explorer.
    2. Navigate to `C:\Users\Lenovo` (or press `Win + R`, type `%userprofile%`, and hit Enter).
    3. Look for `actions.db`.

- **On macOS**:
  - Path: `/Users/YourUsername/actions.db`
  - Example: `/Users/lenovo/actions.db`
  - How to check: Open Finder, press `Cmd + Shift + G`, type `~`, and look for `actions.db`.

- **On Linux**:
  - Path: `/home/YourUsername/actions.db`
  - Example: `/home/lenovo/actions.db`
  - How to check: Open a terminal, type `cd ~` and then `ls -a` to see `actions.db`.

---

### c. Verifying It’s Working
To confirm the database is where it should be and contains data:
1. **Run the Executable**:
   - Execute `dist\pydirector.exe`.
   - Add a few actions via the GUI (e.g., “Test Move”, “move”, “100,200”).

2. **Check the File**:
   - Navigate to the home directory (e.g., `C:\Users\Lenovo`).
   - Look for `actions.db`. It should exist and have a non-zero file size if data was written.

3. **Inspect the Database**:
   - Use a SQLite viewer (e.g., DB Browser for SQLite) to open `actions.db` and verify the `actions` table contains the entries.
   - Or, add a debug print in the code:
     ```python
     def get_actions():
         conn = sqlite3.connect(DB_PATH)
         cursor = conn.cursor()
         cursor.execute('SELECT * FROM actions ORDER BY id')
         actions = cursor.fetchall()
         conn.close()
         print(f"Retrieved actions from {DB_PATH}: {actions}")  # Debug
         return actions
     ```
     Recompile with `--console` and run to see the output.

4. **Check Logs**:
   - Open `pydirector.log` (in the same directory as the executable or wherever it’s configured to write) to see if database operations are logged successfully.

---

### d. Why
- **Design Intent**: By setting `DB_PATH` to the home directory, we ensured the database is stored in a persistent, writable location outside the temporary or build directories. This is what allows data to persist across runs, unlike the original `resource_path('actions.db')` approach that used `sys._MEIPASS`.
- **No Need for `dist`**: The `dist` folder is just for the executable and bundled resources, not runtime-generated files like `actions.db`.

---

## 5.`To keep the "actions.db" in the "dist" Folder`
To keep the `actions.db` in the `dist` folder alongside `pydirector.exe` (e.g., for portability or organization), we can modify `DB_PATH` to point there instead. However, this comes with caveats:

#### Modified Code
```python
import os
import sys

# Set DB_PATH to the directory containing the executable
if getattr(sys, 'frozen', False):  # Running as PyInstaller executable
    BASE_DIR = os.path.dirname(sys.executable)  # Directory of pydirector.exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of pydirector.py
DB_PATH = os.path.join(BASE_DIR, "actions.db")
```

- **Explanation**:
  - `sys.executable`: Path to the running executable (e.g., `C:\path\to\project\dist\pydirector.exe`).
  - `os.path.dirname(sys.executable)`: Extracts the directory (e.g., `C:\path\to\project\dist`).
  - `DB_PATH`: Becomes `C:\path\to\project\dist\actions.db` when compiled.
  - When running with Python, it uses the script’s directory.

- **Caveat**:
  - The `dist` folder must be writable. If we distribute the executable to another location (e.g., `C:\Program Files`), it might fail due to permission issues unless run as admin.
  - For portability, users would need to copy the entire `dist` folder, including `actions.db`, to retain data.

#### Recompile and Test
Recompile with the existing command and run `pydirector.exe` from `dist`. Check if `actions.db` appears there.

---

### Recommendation
- **Keep It in Home Directory**: Storing `actions.db` in `~/actions.db` is safer and more user-friendly, as it avoids permission issues and keeps data tied to the user, not the executable’s location.
- **No Action Needed**: Since it’s working now, there’s no need to change anything unless we have a specific reason to move it to `dist`.

---

### Final Confirmation
To keep everything—including `actions.db`, `target.csv`, and `icon/gear.png`—in the same folder as the executable (`pydirector.exe`). This makes the application portable, meaning users can move the executable and its associated files to any directory and it will still work, as long as the folder remains writable. Here’s how to modify the code and PyInstaller command to achieve this.

---

### Why This Works
- **Executable Directory**: When compiled with PyInstaller, `sys.executable` gives the path to the running executable (e.g., `C:\path\to\dist\pydirector.exe`). Using `os.path.dirname(sys.executable)`, we can dynamically reference the folder containing the executable.
- **Consistency**: By adjusting all file paths (`actions.db`, `target.csv`, `gear.png`) to use this directory, everything stays together.
- **Portability**: Users can copy the entire folder (executable + files) to any location, and the app will still function without hardcoding paths.

---

### Step-by-Step Solution

#### 1. Modify the Code
Update the script to use the executable’s directory as the base path for all files (`actions.db`, `target.csv`, and `gear.png`). Replace `resource_path()` with a new function and adjust `DB_PATH`.

Here’s the revised code snippet for key sections:

```python
import os
import sys

# Determine the base directory (where the executable or script is)
def get_base_path():
    if getattr(sys, 'frozen', False):  # Running as PyInstaller executable
        return os.path.dirname(sys.executable)  # Directory of pydirector.exe
    return os.path.dirname(os.path.abspath(__file__))  # Directory of pydirector.py

BASE_PATH = get_base_path()
DB_PATH = os.path.join(BASE_PATH, "actions.db")

# Update resource_path to use BASE_PATH instead of sys._MEIPASS
def resource_path(relative_path):
    return os.path.join(BASE_PATH, relative_path)

# Database Functions (using DB_PATH)
def create_database(db_name='actions.db'):  # db_name ignored for consistency
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_name TEXT,
            action_type TEXT,
            parameters TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logging.debug(f"Database created at: {DB_PATH}")

def add_action(action_name, action_type, parameters):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO actions (action_name, action_type, parameters, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (action_name, action_type, parameters, timestamp))
    conn.commit()
    conn.close()
    logging.debug(f"Action added: {action_name}")

# Update other database functions similarly (get_actions, update_action, delete_action)

# CSV Reading (update to use resource_path)
def read_target_ids(csv_file='target.csv'):  # Adjusted default to match usage
    csv_path = resource_path(csv_file)
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            target_ids = [row[0] for row in reader]
        return target_ids
    except FileNotFoundError:
        logging.error(f"CSV file not found: {csv_path}")
        print("Error: target.csv not found.")
        return []

# Update tray icon in MainWindow.__init__
self.tray_icon = QSystemTrayIcon(QIcon(resource_path("icon/gear.png")), self)
```

- **Key Changes**:
  - Replaced `resource_path()` logic with `BASE_PATH`, which points to the executable’s directory when bundled or the script’s directory when run with Python.
  - Set `DB_PATH` to `BASE_PATH + "actions.db"`.
  - Updated `read_target_ids()` and tray icon to use `resource_path()` with the new base path.
  - Kept database functions using `DB_PATH`.

#### 2. Update PyInstaller Command
Since we want `target.csv` and `icon/gear.png` in the same folder as the executable, we still need to include them with `--add-data`, but they’ll be accessed from the executable’s directory at runtime.

Use this command:
```
pyinstaller --onefile --windowed --add-data "icon/gear.png;icon" --add-data "target.csv;." --hidden-import=pyautogui --hidden-import=PySide6.QtWidgets --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --icon=icon/gear.png .\pydirector.py
```

- **Notes**:
  - `--add-data "icon/gear.png;icon"`: Includes `gear.png` in the `icon` subfolder of the bundle, which `resource_path("icon/gear.png")` will resolve to.
  - `--add-data "target.csv;."`: Includes `target.csv` in the root of the bundle, which `resource_path("target.csv")` will resolve to.
  - `actions.db` isn’t included because it’s created dynamically at runtime.

#### 3. Test the Setup
1. **Run with Python**:
   - Ensure `target.csv` and `icon/gear.png` are in the same directory as `pydirector.py`.
   - Run `python pydirector.py`.
   - Add actions and check that `actions.db` appears in the same directory as `pydirector.py`.

2. **Compile and Run**:
   - Run the PyInstaller command above.
   - Go to `dist`, where we can see `pydirector.exe`.
   - Copy `target.csv` and `icon/gear.png` from the project folder to `dist` (or a subfolder like `icon/` for `gear.png`) manually after building, since `--onefile` doesn’t leave them there automatically:
     ```
     dist/
     ├── pydirector.exe
     ├── target.csv
     └── icon/
         └── gear.png
     ```
   - Run `pydirector.exe`.
   - Add actions and confirm `actions.db` is created in `dist` alongside `pydirector.exe`.

3. **Verify Portability**:
   - Move the entire `dist` folder to another location (e.g., `D:\TestFolder`).
   - Run `pydirector.exe` from there and ensure it still works (reads `target.csv`, uses `gear.png`, and writes to `actions.db` in the new location).

---

### What Happens at Runtime
- **Script Mode (`python pydirector.py`)**:
  - `BASE_PATH` = directory of `pydirector.py`.
  - `DB_PATH` = `<script_dir>/actions.db`.
  - `resource_path("target.csv")` = `<script_dir>/target.csv`.
  - `resource_path("icon/gear.png")` = `<script_dir>/icon/gear.png`.

- **Executable Mode (`pydirector.exe`)**:
  - `BASE_PATH` = directory of `pydirector.exe` (e.g., `C:\path\to\dist`).
  - `DB_PATH` = `C:\path\to\dist\actions.db`.
  - `resource_path("target.csv")` = `C:\path\to\dist\target.csv` (extracted from bundle).
  - `resource_path("icon/gear.png")` = `C:\path\to\dist\icon\gear.png` (extracted from bundle).

---

### Caveats
- **Write Permissions**: The executable’s directory must be writable for `actions.db` to be created/updated. If we place it in a restricted location (e.g., `C:\Program Files`), it might fail unless run as admin.
- **Manual File Placement**: After building with `--onefile`, PyInstaller doesn’t leave `target.csv` and `gear.png` in `dist`—they’re embedded in the executable. We will need to manually copy them to `dist` (or distribute them with the executable) for the app to find them at runtime.

#### Alternative: `--onedir` Mode
If we want PyInstaller to automatically place all files in `dist` without manual copying, use `--onedir` instead:
```
pyinstaller --onedir --windowed --add-data "icon/gear.png;icon" --add-data "target.csv;." --hidden-import=pyautogui --hidden-import=PySide6.QtWidgets --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --icon=icon/gear.png .\pydirector.py
```
- Result: `dist/pydirector/` contains `pydirector.exe`, `target.csv`, `icon/gear.png`, and dependencies. `actions.db` will be created there too.
- Trade-off: Larger folder instead of a single file, but simpler



___

Let’s compare the two approaches for handling file paths in the PyInstaller-compiled application: the original `resource_path()` function we used versus the updated approach with `get_base_path()` that I suggested for keeping everything in the same folder as the executable. I’ll break down their mechanics, implications, and suitability for the goal of keeping all files (`actions.db`, `target.csv`, `icon/gear.png`) alongside `pydirector.exe`.

---

### Original Approach: `resource_path()`
```python
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
```

#### How It Works
- **When Running as a Script (`python pydirector.py`)**:
  - `hasattr(sys, '_MEIPASS')` is `False` because `_MEIPASS` only exists in a PyInstaller bundle.
  - `os.path.abspath(".")`: Returns the absolute path of the current working directory (where we ran the script from, e.g., `C:\path\to\project` if we ran `python pydirector.py` there).
  - `os.path.join(os.path.abspath("."), relative_path)`: Combines the current directory with `relative_path` (e.g., `"actions.db"`, `"target.csv"`, `"icon/gear.png"`).
  - Example: If run from `C:\path\to\project`, `resource_path("actions.db")` → `C:\path\to\project\actions.db`.

- **When Running as a PyInstaller Executable (`pydirector.exe`)**:
  - `hasattr(sys, '_MEIPASS')` is `True` because PyInstaller sets `_MEIPASS` to a temporary directory where bundled files are extracted (e.g., `C:\Users\Lenovo\AppData\Local\Temp\_MEIxxxx`).
  - `os.path.join(sys._MEIPASS, relative_path)`: Combines the temporary directory with `relative_path`.
  - Example: `resource_path("actions.db")` → `C:\Users\Lenovo\AppData\Local\Temp\_MEIxxxx\actions.db`.

#### Implications
1. **Script Mode**:
   - Works fine for `target.csv` and `icon/gear.png` if they’re in the current directory.
   - `actions.db` is created in the current working directory (e.g., `C:\path\to\project`), which is persistent and writable, so data is saved across runs.

2. **Executable Mode (`--onefile`)**:
   - **Pros**: Correctly locates bundled files (`target.csv`, `icon/gear.png`) in the temporary directory if included with `--add-data`.
   - **Cons**:
     - `actions.db` is created in `sys._MEIPASS`, which is:
       - **Temporary**: Deleted when the app closes, so data doesn’t persist.
       - **Read-Only for SQLite**: SQLite often fails to write reliably in this directory due to its nature, causing the original issue.
     - Files are scattered: Bundled files are in `sys._MEIPASS`, but `actions.db` isn’t in the `dist` folder or alongside the executable.

3. **Portability**:
   - Poor for `actions.db`: Data is lost because it’s tied to a temporary location.
   - Requires manual placement of `target.csv` and `gear.png` alongside the executable post-build, but they’re accessed from `sys._MEIPASS`.

---

### New Approach: `get_base_path()`
```python
def get_base_path():
    if getattr(sys, 'frozen', False):  # Running as PyInstaller executable
        return os.path.dirname(sys.executable)  # Directory of pydirector.exe
    return os.path.dirname(os.path.abspath(__file__))  # Directory of pydirector.py

BASE_PATH = get_base_path()

def resource_path(relative_path):
    return os.path.join(BASE_PATH, relative_path)

DB_PATH = os.path.join(BASE_PATH, "actions.db")
```

#### How It Works
- **When Running as a Script (`python pydirector.py`)**:
  - `getattr(sys, 'frozen', False)` is `False` (PyInstaller’s flag for bundled apps isn’t set).
  - `os.path.abspath(__file__)`: Returns the absolute path of `pydirector.py` (e.g., `C:\path\to\project\pydirector.py`).
  - `os.path.dirname(...)`: Extracts the directory (e.g., `C:\path\to\project`).
  - `BASE_PATH`: `C:\path\to\project`.
  - Examples:
    - `DB_PATH` → `C:\path\to\project\actions.db`.
    - `resource_path("target.csv")` → `C:\path\to\project\target.csv`.
    - `resource_path("icon/gear.png")` → `C:\path\to\project\icon\gear.png`.

- **When Running as a PyInstaller Executable (`pydirector.exe`)**:
  - `getattr(sys, 'frozen', False)` is `True` (set by PyInstaller).
  - `sys.executable`: Path to the executable (e.g., `C:\path\to\dist\pydirector.exe`).
  - `os.path.dirname(sys.executable)`: Directory of the executable (e.g., `C:\path\to\dist`).
  - `BASE_PATH`: `C:\path\to\dist`.
  - Examples:
    - `DB_PATH` → `C:\path\to\dist\actions.db`.
    - `resource_path("target.csv")` → `C:\path\to\dist\target.csv`.
    - `resource_path("icon/gear.png")` → `C:\path\to\dist\icon\gear.png`.

#### Implications
1. **Script Mode**:
   - All files (`actions.db`, `target.csv`, `gear.png`) are created/accessed in the script’s directory (e.g., `C:\path\to\project`).
   - Consistent with the original working setup when running with Python.

2. **Executable Mode (`--onefile`)**:
   - **Pros**:
     - All files are tied to the executable’s directory (e.g., `C:\path\to\dist`), which is persistent and can be writable (if not in a restricted location like `C:\Program Files`).
     - `actions.db` is created alongside `pydirector.exe`, solving the persistence issue.
     - Portable: Move the `dist` folder anywhere, and everything stays together.
   - **Cons**:
     - Requires `target.csv` and `gear.png` to be manually placed in `dist` post-build (or distributed with the executable) since `--onefile` embeds them in the executable but doesn’t leave them in `dist`.
     - Directory must be writable, or SQLite writes will fail (e.g., needs admin rights in restricted folders).

3. **Portability**:
   - Excellent: The entire app (executable + files) can be moved as a single unit, and it will work as long as the folder is writable.

---

### Comparison Table

| **Aspect**                   | **Original (`resource_path`)**                         | **New (`get_base_path`)**                     |
| ---------------------------- | ------------------------------------------------------ | --------------------------------------------- |
| **Script Mode Location**     | Current working directory (e.g., `C:\path\to\project`) | Script directory (e.g., `C:\path\to\project`) |
| **Executable Mode Location** | Temporary dir (`sys._MEIPASS`)                         | Executable dir (e.g., `C:\path\to\dist`)      |
| **Database Persistence**     | No (temp dir deleted on exit)                          | Yes (stored alongside executable)             |
| **File Access**              | Bundled files in `sys._MEIPASS`, DB elsewhere          | All files in executable’s dir                 |
| **Portability**              | Poor (DB lost, files scattered)                        | High (everything moves together)              |
| **Setup Effort**             | Simple but flawed for DB                               | Requires manual file placement post-build     |
| **Write Permission Issues**  | High (temp dir often read-only)                        | Possible (if dir is restricted)               |

---

### Why `get_base_path()` Meets the Goal
We want to keep all the files in the same folder where the executable is. But, the original `resource_path()` fails at this because:
- It puts `actions.db` in a temporary directory that’s deleted, not alongside `pydirector.exe`.
- While it accesses bundled `target.csv` and `gear.png` correctly from `sys._MEIPASS`, it doesn’t align them with the database’s location.

The `get_base_path()` approach:
- Ensures `actions.db`, `target.csv`, and `gear.png` are all referenced relative to the executable’s directory (e.g., `C:\path\to\dist`).
- Makes the app portable by keeping everything together in a single, persistent folder.

---

### Addressing the `--onefile` Limitation
With `--onefile`, PyInstaller embeds `target.csv` and `gear.png` inside `pydirector.exe` and extracts them to `sys._MEIPASS` at runtime. However, the code looks for them in `BASE_PATH` (e.g., `C:\path\to\dist`), not `sys._MEIPASS`.

#### Option 1: Manual File Placement
- After building, copy `target.csv` and `icon/gear.png` to `dist`:
  ```
  dist/
  ├── pydirector.exe
  ├── target.csv
  └── icon/
      └── gear.png
  ```
- Run `pydirector.exe`, and `actions.db` will be created there too.

#### Option 2: Use `--onedir` Mode
- Command:
  ```
  pyinstaller --onedir --windowed --add-data "icon/gear.png;icon" --add-data "target.csv;." --hidden-import=pyautogui --hidden-import=PySide6.QtWidgets --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --icon=icon/gear.png .\pydirector.py
  ```
- Result: `dist/pydirector/` contains all files automatically:
  ```
  dist/pydirector/
  ├── pydirector.exe
  ├── target.csv
  ├── icon/
  │   └── gear.png
  └── [other PyInstaller dependencies]
  ```
- `actions.db` will be created in the same folder.

#### Option 3: Hybrid Approach
- Keep `--onefile` and modify `resource_path()` to use `sys._MEIPASS` for read-only files (`target.csv`, `gear.png`) but `BASE_PATH` for `actions.db`:
  ```python
  def resource_path(relative_path):
      if hasattr(sys, '_MEIPASS'):
          return os.path.join(sys._MEIPASS, relative_path)  # For bundled files
      return os.path.join(BASE_PATH, relative_path)
  
  DB_PATH = os.path.join(BASE_PATH, "actions.db")  # Always alongside executable
  ```
- This keeps `target.csv` and `gear.png` bundled but places `actions.db` in `dist`.

---

### Recommendation
- **For Simplicity**: Use `--onedir` with `get_base_path()`. Everything is automatically placed in `dist/pydirector/`, and it’s portable.
- **For Single File**: Use `--onefile` with manual placement (Option 1) or the hybrid approach (Option 3). 



## 5. How does the code work ???

### How the Code Works

"PyDirector," is a GUI-based automation tool built with PySide6 (Qt for Python), PyAutoGUI, SQLite, and other libraries. It allows users to define, manage, and execute mouse/keyboard automation actions stored in a database, optionally looping over a list of target IDs from a CSV file. Here’s a detailed breakdown:

#### 1. **Imports and Setup**
- **Libraries**: 
  - `sys`, `os`: Handle file paths and executable behavior (e.g., PyInstaller support).
  - `sqlite3`: Manage a database for storing actions.
  - `datetime`, `time`: Handle timestamps and delays.
  - `csv`: Read target IDs from a CSV file.
  - `logging`: Log events to `pydirector.log` for debugging.
  - `PySide6`: Build the GUI (QMainWindow, QTableWidget, etc.).
  - `pyautogui`: Perform automation tasks (mouse movement, clicks, typing, etc.).
- **Logging**: Configured to write debug/info/error messages to `pydirector.log`.
- **Paths**: 
  - `get_base_path()` and `resource_path()` ensure the script works whether run as a Python file or a PyInstaller executable.
  - `DB_PATH` points to `actions.db` in the base directory.

#### 2. **Database Management**
- **Schema**: The `actions` table in `actions.db` has columns: `id`, `action_name`, `action_type`, `parameters`, `timestamp`.
- **Functions**:
  - `create_database()`: Creates the table if it doesn’t exist.
  - `add_action()`, `update_action()`, `delete_action()`: CRUD operations for actions.
  - `get_actions()`: Retrieves all actions for display or execution.

#### 3. **CSV Handling**
- `read_target_ids()`: Reads a single-column CSV file (`target.csv`) to get a list of target IDs. These IDs can be used in actions (e.g., typing them).

#### 4. **Automation Logic**
- **Core Function**: `execute_action(action, target_id=None)`:
  - Takes an action tuple from the database (`id`, `name`, `type`, `parameters`, `timestamp`) and an optional `target_id`.
  - Supports these `action_type`s:
    - `move`: Moves mouse to `(x, y)` with `duration=0.5`.
    - `click`: Single click (`left` or `right`).
    - `double_click`: Double click (`left` or `right`).
    - `right_click`: Right-click at current position.
    - `drag`: Drags mouse to `(x, y)` with `duration=0.5`.
    - `hotkey`: Presses key combinations (e.g., `ctrl,c`).
    - `type`: Types text, optionally replacing `{target_id}` with the CSV value.
    - `wait`: Pauses for specified seconds.
  - Errors are logged and printed if an action fails.
- **Run Function**: `run_automation(loop_count=0, stop_flag=None)`:
  - Loads target IDs and actions.
  - Loops either over all target IDs (`loop_count=0`) or a specified number of times.
  - For each loop:
    - Picks a `target_id` (from CSV or loop index).
    - Executes all actions sequentially, passing the `target_id`.
    - Adds a `time.sleep(1.0)` between actions.
  - Stops if `stop_flag()` returns `True` (e.g., Esc pressed).

#### 5. **GUI (MainWindow)**
- **Components**:
  - **Mouse Position Label**: Updates every 100ms via a `QTimer`.
  - **Table**: Displays actions from the database.
  - **Buttons**: Add, Edit, Delete actions; Start automation.
  - **Loop Input**: A QSpinBox to set the number of loops (0 = use all target IDs).
  - **System Tray**: Minimizes to tray with Show/Quit options.
  - **Shortcut**: Esc key stops automation.
- **Behavior**:
  - Minimizes to tray on close; double-click tray icon to restore.
  - Actions are managed via an `ActionDialog` popup.
  - Automation hides the window, runs, and shows a tray notification when done/interrupted.

#### 6. **Execution Flow**
1. User adds actions via GUI (e.g., "Move to 100,200", "Type Hello").
2. User sets loop count and clicks "Start Automation".
3. Script reads `target.csv`, executes actions for each target ID, and logs progress.
4. User can press Esc to stop; tray notifications report the outcome.

---

### Controlling the Interval Between Actions

#### Current Timing Control
- **Between Actions**: In `run_automation()`, there’s a hardcoded `time.sleep(1.0)` after each `execute_action()` call. This means a **1-second delay** separates the end of one action from the start of the next, regardless of the action type.
- **Within Actions**: For `move` and `drag` actions, `pyautogui.moveTo()` and `pyautogui.dragTo()` use `duration=0.5`, which controls how long the mouse takes to reach its destination (0.5 seconds). Other actions (e.g., `click`, `type`) execute instantly or at PyAutoGUI’s default speed.

#### Is `duration` a Method to Control Intervals?
- **Not Directly for Intervals Between Actions**: The `duration` parameter in `moveTo` and `dragTo` controls the **duration of the movement itself**, not the pause between actions. For example:
  - `pyautogui.moveTo(100, 200, duration=0.5)` takes 0.5 seconds to move the mouse, then the script immediately proceeds to `time.sleep(1.0)` before the next action.
  - Changing `duration` affects how “smooth” or “slow” the movement looks, not the gap between actions.
- **Suitable for Specific Actions**: It’s a timing control only for `move` and `drag`, not for `click`, `type`, etc., which don’t use `duration`.

#### How to Control the Interval Between Actions
To adjust the timing **between** actions (the pause after one action completes and before the next begins), you have these options:

1. **Modify the `time.sleep(1.0)` in `run_automation`**:
   - Current code:
     ```python
     for action in actions:
         if stop_flag and stop_flag():
             return False
         logging.debug(f"Executing action: {action}")
         execute_action(action, target_id)
         time.sleep(1.0)  # Fixed 1-second delay
     ```
   - Change `1.0` to your desired delay (e.g., `0.5` for 0.5 seconds, `2.0` for 2 seconds):
     ```python
     time.sleep(0.5)  # Now 0.5 seconds between actions
     ```

2. **Make the Delay Configurable**:
   - Add a UI element (e.g., a QSpinBox) for users to set the delay:
     ```python
     # In MainWindow.__init__
     self.delay_label = QLabel("Delay Between Actions (seconds):")
     self.delay_input = QSpinBox()
     self.delay_input.setMinimum(0)
     self.delay_input.setMaximum(10)  # Max 10 seconds
     self.delay_input.setValue(1)  # Default 1 second
     self.layout.addWidget(self.delay_label)
     self.layout.addWidget(self.delay_input)
     ```
   - Update `run_automation` to use this value:
     ```python
     def start_automation(self):
         loop_count = self.loop_input.value()
         delay = self.delay_input.value()  # Get delay from UI
         self.is_running = True
         self.stop_requested = False
         self.hide()
         logging.debug(f"Starting automation with {loop_count} loops and {delay} sec delay")
         print("Automation started. Press Esc to stop.")
         completed = run_automation(loop_count, delay, stop_flag=lambda: self.stop_requested)
         self.is_running = False
         # ... rest of the method ...

     def run_automation(loop_count=0, delay=1.0, stop_flag=None):
         # ... existing code ...
         for action in actions:
             if stop_flag and stop_flag():
                 return False
             logging.debug(f"Executing action: {action}")
             execute_action(action, target_id)
             time.sleep(delay)  # Use configurable delay
         # ... rest of the function ...
     ```

3. **Store Delay in the Database**:
   - Add a `delay_after` column to the `actions` table:
     ```python
     def create_database(db_name='actions.db'):
         conn = sqlite3.connect(DB_PATH)
         cursor = conn.cursor()
         cursor.execute('''
             CREATE TABLE IF NOT EXISTS actions (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 action_name TEXT,
                 action_type TEXT,
                 parameters TEXT,
                 delay_after REAL DEFAULT 1.0,  -- New column
                 timestamp TEXT
             )
         ''')
         conn.commit()
         conn.close()
     ```
   - Update `add_action`, `update_action`, and `ActionDialog` to include `delay_after`.
   - Modify `run_automation` to use each action’s delay:
     ```python
     for action in actions:
         if stop_flag and stop_flag():
             return False
         logging.debug(f"Executing action: {action}")
         execute_action(action, target_id)
         time.sleep(action[4])  # Use delay_after from database
     ```

#### Total Time Between Actions
The effective interval between the start of one action and the start of the next is:
- **Action Execution Time** (e.g., 0.5 seconds for `move` with `duration=0.5`, near-instant for `click`) + **Delay** (currently 1.0 second).
- Example:
  - `moveTo(100, 200, duration=0.5)`: 0.5s movement + 1.0s sleep = **1.5s total**.
  - `click()`: ~0s execution + 1.0s sleep = **1.0s total**.

#### Recommendation
- **Best Approach**: Modify `time.sleep(1.0)` or make it configurable via the UI (Option 2). This gives you flexibility without overcomplicating the database.
- **Duration’s Role**: Use `duration` to fine-tune `move` and `drag` speeds, but rely on `time.sleep()` for the interval between all actions.

---

### Example Modification
Here’s how you could implement a configurable delay:
```python
# In MainWindow.__init__, after loop_input:
self.delay_label = QLabel("Delay Between Actions (seconds):")
self.delay_input = QSpinBox()
self.delay_input.setMinimum(0)
self.delay_input.setMaximum(10)
self.delay_input.setValue(1)
self.layout.addWidget(self.delay_label)
self.layout.addWidget(self.delay_input)

# Update start_automation:
def start_automation(self):
    loop_count = self.loop_input.value()
    delay = self.delay_input.value()
    self.is_running = True
    self.stop_requested = False
    self.hide()
    logging.debug(f"Starting automation with {loop_count} loops and {delay} sec delay")
    print("Automation started. Press Esc to stop.")
    completed = run_automation(loop_count, delay, stop_flag=lambda: self.stop_requested)
    self.is_running = False
    # ... rest of the method ...

# Update run_automation signature:
def run_automation(loop_count=0, delay=1.0, stop_flag=None):
    # ... existing code ...
    for action in actions:
        if stop_flag and stop_flag():
            return False
        logging.debug(f"Executing action: {action}")
        execute_action(action, target_id)
        time.sleep(delay)  # Configurable delay
    # ... rest of the function ...
```

Now, users can set the delay (0-10 seconds) in the GUI, and it applies uniformly between actions.

---

### Final Thoughts
To control intervals, tweaking `time.sleep()` is the most straightforward and effective method.


## 7. `Todo`

- Add `interruption` in the middle of running (CTRL-C seems taking no effect)
