# OptoStim2P

OptoStim2P is a PyQt5 desktop tool for two-photon stimulation workflows. It provides stimulation control, XY/Z registration utilities, live/reference ROI preview, post-stimulation activation checks, and PyAutoGUI-based interaction with microscope software.

## Current Entry Point

- Main source file: `V5.1.2.py`
- App title: `OptoStim2P v5.1.2`
- Default settings file: `app_settings.json`

## Recommended Environment

The current Windows build has been tested with a PyQt5 conda environment similar to:

```powershell
D:\anaconda3\envs\pyqt5\python.exe
```

Required packages include PyQt5, numpy, opencv-python, matplotlib, tifffile, pynput, pyautogui, pyperclip, and PyInstaller for packaging.

## Run From Source

```powershell
D:\anaconda3\envs\pyqt5\python.exe F:\Code\OptoStim\V5.1.2.py
```

## Syntax Check

```powershell
D:\anaconda3\envs\pyqt5\python.exe -m py_compile F:\Code\OptoStim\V5.1.2.py
```

## Package Windows Exe

```powershell
D:\anaconda3\envs\pyqt5\python.exe -m PyInstaller --noconfirm --clean OptoStim2P_v5.1.2.spec
```

The generated `build/` and `dist/` folders are intentionally ignored by Git. Publish packaged executables through GitHub Releases rather than committing them to the source repository.
