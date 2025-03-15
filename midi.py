import threading
import time
import atexit
import keyboard
import os

# Import our components
from comps.volume_osd import VolumeOSD
from comps.midi_control import (
    connect_xtouch, disconnect_xtouch, process_xtouch_messages, 
    get_connection_status
)
from comps.volume_control import VolumeControl
from comps.system_tray import SystemTray

# Global variables
midi_thread = None
exit_flag = False
volume_osd = None
system_tray = None
volume_control = None

def handle_keyboard_shortcuts(e):
    """Handle keyboard shortcuts for connecting/disconnecting X-Touch Mini"""
    # Ctrl+Page Down to release X-Touch Mini
    if keyboard.is_pressed('ctrl') and e.name == 'page down':
        if get_connection_status():
            print("Keyboard shortcut: Releasing X-Touch Mini")
            disconnect_xtouch()
            if system_tray:
                system_tray.update_connection_status(get_connection_status())
    
    # Ctrl+Page Up to reconnect X-Touch Mini
    elif keyboard.is_pressed('ctrl') and e.name == 'page up':
        if not get_connection_status():
            print("Keyboard shortcut: Reconnecting X-Touch Mini")
            connect_xtouch()
            if system_tray:
                system_tray.update_connection_status(get_connection_status())

def cleanup():
    """Cleanup function to release resources on exit"""
    global exit_flag, system_tray, volume_osd
    print("\nCleaning up resources...")
    exit_flag = True
    disconnect_xtouch()
    
    # First stop the icon (which might be waiting on user interaction)
    if system_tray:
        system_tray.stop()
    
    # Then clean up the volume OSD
    if volume_osd:
        try:
            volume_osd.destroy()
        except Exception as e:
            print(f"Error destroying volume OSD: {e}")
    
    print("Cleanup complete. Goodbye!")

def exit_app(icon):
    """Exit the application from the tray menu"""
    cleanup()
    # Use a more gentle exit that doesn't interrupt ongoing threads abruptly
    if icon:
        icon.stop()
    # Give threads time to clean up before forcing exit
    threading.Timer(0.5, lambda: os._exit(0)).start()

def get_exit_flag():
    """Getter for exit_flag to avoid global variable issues"""
    global exit_flag
    return exit_flag

# Main function
def main():
    global midi_thread, exit_flag, volume_osd, system_tray, volume_control
    
    try:
        # Initialize volume control
        volume_control = VolumeControl()
        
        # Initialize volume OSD
        volume_osd = VolumeOSD()
        
        # Set up system tray icon with callbacks
        system_tray = SystemTray(
            connect_func=lambda: connect_xtouch() and system_tray.update_connection_status(get_connection_status()),
            disconnect_func=lambda: disconnect_xtouch() and system_tray.update_connection_status(get_connection_status()),
            exit_func=exit_app
        )
        system_tray.setup(get_connection_status)
        
        # Connect to X-Touch Mini on startup
        if not connect_xtouch():
            print("Failed to connect to X-Touch Mini on startup")
            print("You can try reconnecting with Ctrl+Page Up or from the tray menu")
        
        # Update connection status in tray menu
        system_tray.update_connection_status(get_connection_status())
        
        # Start monitoring keyboard shortcuts
        keyboard.on_release(handle_keyboard_shortcuts)
        
        # Start X-Touch Mini processing thread
        midi_thread = threading.Thread(
            target=process_xtouch_messages, 
            args=(get_exit_flag, volume_control, volume_osd),
            daemon=True
        )
        midi_thread.start()
        
        print("\nX-Touch Mini controller is active:")
        print("- The application is now running in the system tray")
        print("- Press Ctrl+Page Down to release the X-Touch Mini")
        print("- Press Ctrl+Page Up to reconnect the X-Touch Mini")
        print("- Right-click the tray icon to access the menu")
        
        # Keep main thread alive until interrupted
        while not exit_flag:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting program - bye!")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Make sure to set exit flag in case of any exit
        exit_flag = True
        if midi_thread and midi_thread.is_alive():
            midi_thread.join(timeout=1.0)

# Register cleanup function to run on exit
atexit.register(cleanup)

if __name__ == "__main__":
    main()