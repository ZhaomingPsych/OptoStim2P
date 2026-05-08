# OptoStim2P

OptoStim2P is a PyQt5 desktop tool for two-photon optogenetic stimulation workflows. It supports stimulation-site registration, XY/Z alignment, single-cell preview, automated stimulation control, and post-stimulation activation checks.

## Microscope Software

OptoStim2P is designed for use with Olympus microscope software, specifically the Olympus FV31S-SW workflow used in our experiments.

## Developers

Developed by Qiyuan Liang and Ming Zhao at Shenzhen Bay Laboratory.

## Current Version

- App version: `OptoStim2P v5.1.2`
- Main source file: `V5.1.2.py`
- Default settings file: `app_settings.json`

## Run From Source

The current source version is developed and tested on Windows with a PyQt5 conda environment.

```powershell
D:\anaconda3\envs\pyqt5\python.exe F:\Code\OptoStim\V5.1.2.py
```

Core dependencies include PyQt5, numpy, opencv-python, matplotlib, tifffile, pynput, pyautogui, and pyperclip.

## Windows Release

Packaged Windows builds are distributed through GitHub Releases instead of being committed to the source repository.

Download the release zip, extract the full folder, and run:

```text
OptoStim2P_v5.1.2.exe
```

Do not run the executable directly from inside the zip archive. The full extracted folder is required because the Windows build uses a PyInstaller onedir layout.

## Developer Notes

`build/`, `dist/`, local manuals, caches, screenshots, and packaged binaries are intentionally ignored by Git. Source changes should be committed separately from release artifacts.
