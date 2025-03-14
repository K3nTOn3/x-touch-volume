# MIDI Volume Control for Behringer X-Touch Mini

A Python application that allows you to control your computer's master volume using the Behringer X-Touch Mini MIDI controller. This app specifically maps the volume slider on layer A (controller 9 on MIDI channel 11) to adjust system volume.

## Features

- Control system volume directly from your Behringer X-Touch Mini
- System tray integration for easy access
- Keyboard shortcuts for quick connection/disconnection
- Automatic connection to the X-Touch Mini
- Visual feedback on volume changes

## Requirements

- Python 3.6+
- Behringer X-Touch Mini MIDI controller
- Required Python packages:
  - mido
  - pycaw
  - comtypes
  - keyboard
  - pystray
  - Pillow (PIL)

## Installation

1. Make sure you have Python installed on your system
2. Install the required packages:
   ```
   pip install mido python-rtmidi pycaw comtypes keyboard pystray pillow
   ```
3. Download or clone this repository to your local machine

## Auto-Start on Windows Boot

To make the application start automatically when Windows boots:

1. Press `Win + R` and type `shell:startup` to open the Windows Startup folder
2. Right-click in the folder and select "New > Shortcut"
3. For the location, enter the following command:
   ```
   pythonw.exe "[PATH_TO_YOUR_SCRIPT]\midi.py"
   ```
   - Replace `[PATH_TO_YOUR_SCRIPT]` with the actual path to where you saved the midi.py file

### Finding pythonw.exe

If the shortcut doesn't work without specifying the full path to pythonw.exe:

1. Open Command Prompt and type:
   ```
   where pythonw
   ```
2. This will show the full path to pythonw.exe on your system
3. Use the full path in your shortcut:
   ```
   C:\Path\To\Your\pythonw.exe "[PATH_TO_YOUR_SCRIPT]\midi.py"
   ```

### Why Use pythonw.exe Instead of python.exe

- `pythonw.exe` runs Python scripts without showing a console window
- This allows the application to run silently in the background
- Only the system tray icon will be visible, providing a cleaner user experience
- The application will still function normally and can be controlled via the system tray icon

## Usage

1. Connect your Behringer X-Touch Mini to your computer via USB
2. Run the application:
   ```
   python midi.py
   ```
3. The application will start and appear in the system tray
4. Use the volume slider on layer A of your X-Touch Mini to adjust system volume
5. Right-click the system tray icon to access the application menu

## Keyboard Shortcuts

- **Ctrl+Page Up**: Reconnect the X-Touch Mini
- **Ctrl+Page Down**: Disconnect the X-Touch Mini

## X-Touch Mini Setup

This application is preconfigured to work with the X-Touch Mini in default mode:
- The volume slider on layer A (identified as controller 9 on channel 11 in MIDI)
- Make sure your X-Touch Mini is set to layer A for proper functionality
- No custom configuration is needed - the application works with the default X-Touch Mini settings

## Troubleshooting

If you have trouble connecting to your X-Touch Mini:

1. Make sure your X-Touch Mini is properly connected via USB
2. Check if you need to install the X-Touch Mini drivers from Behringer's website
3. Try running the program as administrator
4. Check Windows Device Manager to see if the device is recognized
5. Ensure no other application is using the X-Touch Mini MIDI device
6. Try unplugging and reconnecting the X-Touch Mini

## System Tray Menu

- **Connected status**: Shows whether the X-Touch Mini is currently connected
- **Connect MIDI**: Manually connect to the X-Touch Mini
- **Disconnect MIDI**: Manually disconnect from the X-Touch Mini
- **Exit**: Close the application

## Notes

The application automatically connects to the first available MIDI device, assuming it's the X-Touch Mini. If you have multiple MIDI devices connected, you may need to modify the source code to select the correct device.
