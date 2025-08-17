AYA COPAS
AYA COPAS is a Python-based GUI application designed to efficiently copy files and folders with a user-friendly interface. It supports both single-file and folder copying, with optimized performance for small, medium, and large files. The application uses a hybrid copying approach, leveraging multi-threading for smaller files and sequential copying for large files to ensure efficient resource usage.
Features

Flexible Copying Options:
Single File Mode: Copy individual files with progress tracking and overwrite confirmation.
Folder Mode: Copy entire folder structures, preserving directory hierarchies.


Optimized Performance:
Automatically adjusts buffer sizes based on file size (4MB to 64MB).
Uses multi-threading for small and medium files (<800MB) to maximize CPU utilization.
Processes large files (>800MB) sequentially to avoid memory overload.


User-Friendly GUI: Built with Tkinter, featuring:
Source and destination path selection with browse dialogs.
Real-time progress bar, speed, ETA, and file count updates.
Cancel operation support.


Custom Icon: Uses a custom AYA.ico icon for the application window and executable (Windows).
Cross-Platform: Primarily designed for Windows but adaptable for other platforms with minor modifications.
File Metadata Preservation: Maintains file timestamps after copying.
Smart Overwrite Handling: Skips identical files (same size and modification time) to save time.

Requirements

Python 3.6 or later
Tkinter (included with standard Python installations; may require python3-tk on Linux)
AYA.ico icon file (included in the project directory for the application icon)
Py OD IDE (optional, for running in the browser)
PyInstaller (optional, for building the executable)

Setup Instructions
1. Clone or Download the Repository
Download the project files, including aya_copas.py (or rename the provided script) and AYA.ico, to your local machine.
2. Set Up a Virtual Environment
Create and activate a virtual environment to isolate dependencies:
cd /path/to/project
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Verify Tkinter
Ensure Tkinter is available. It’s included with Python, but on Linux, you may need to install it:

Ubuntu/Debian:sudo apt-get install python3-tk


Fedora:sudo dnf install python3-tkinter



4. Run the Application
Run the script directly:
python aya_copas.py

5. Build a One-File Executable (Optional)
To create a standalone executable, use PyInstaller:
pip install pyinstaller
pyinstaller --onefile --add-data "AYA.ico;." --icon=AYA.ico --name=AYA_COPAS --noconsole aya_copas.py


On Linux/macOS, use : instead of ; in --add-data, e.g., --add-data "AYA.ico:.".
The executable (AYA_COPAS.exe on Windows) will be in the dist directory.

Usage

Launch the Application: Run aya_copas.py or the compiled executable.
Select Source Type:
Choose File to copy a single file.
Choose Folder to copy an entire directory and its contents.


Select Paths:
Click "Browse" next to "Source" to select the file or folder to copy.
Click "Browse" next to "Destination" to select the destination path.
For single files, the destination defaults to the source file’s directory (you can override it with a specific file path).


Start Copying: Click "Start Copy" to begin the operation.
The progress bar, speed (MB/s), ETA, and file count will update in real-time.
For folders, directories are created automatically, and files are copied with optimized buffer sizes.


Cancel Operation: Click "Cancel" to stop the copying process.
Monitor Status: The status label displays the current operation state (e.g., "Copying...", "Completed!", or "Error").

Project Structure
project_directory/
├── aya_copas.py         # Main Python script
├──ＡＹＡ.ico              # Application icon
├── dist/                # Output directory for executable (after building)
├── venv/                # Virtual environment directory
└── README.md            # This file

Notes

Icon: Ensure AYA.ico is in the project directory. If the icon doesn’t load, check console logs for errors in _get_resource_path.
Windows-Specific Features: The application sets a custom Windows application ID for taskbar grouping. This is ignored on non-Windows platforms.
Cross-Platform: For Linux/macOS, you may need to replace .ico with a .png icon and modify _set_app_icon:if sys.platform.startswith('win'):
    window.iconbitmap(self._get_resource_path('AYA.ico'))
else:
    icon = PhotoImage(file=self._get_resource_path('AYA.png'))
    window.iconphoto(True, icon)

Update the PyInstaller --add-data option to include AYA.png.
Error Handling: Errors during copying (e.g., file access issues) are displayed in a message box and printed to the console.
Performance: The application uses dynamic worker counts based on CPU cores and file count, with a maximum of 64 workers for large folder operations.

Troubleshooting

Icon Not Displayed: Verify AYA.ico is in the project directory and included in the PyInstaller bundle. Check console logs for warnings.
Tkinter Not Found: Install python3-tk on Linux or verify your Python installation.
PyInstaller Issues: Update PyInstaller (pip install --upgrade pyinstaller) or check the dist directory for the executable.
Copy Errors: Ensure source and destination paths are accessible and not locked by other processes. Avoid selecting the same source and destination.
Performance Issues: For very large folders, copying may take time due to the number of files or disk speed. Check CPU and disk usage.

License
This project is licensed under the MIT License. See the LICENSE file for details (if applicable).
Contact
For issues or suggestions, please contact the developer at [etriowidodo@mail.com].