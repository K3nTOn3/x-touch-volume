import mido
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import keyboard
import threading
import atexit
import pystray
from PIL import Image, ImageDraw
import os

# Global variables
inport = None
connected = False
midi_thread = None
exit_flag = False
icon = None

# Set up volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get current volume (value between 0.0 and 1.0)
current_volume = volume.GetMasterVolumeLevelScalar()
print(f"Current volume: {current_volume * 100:.0f}%")

def connect_xtouch():
    """Connect to the X-Touch Mini controller"""
    global inport, connected
    
    try:
        # Handle case where device might be visible but not accessible
        if connected and inport:
            print("Already connected.")
            return True
            
        ports = mido.get_input_names()
        if not ports:
            print("No X-Touch Mini detected. Please connect your X-Touch Mini and try again.")
            return False
        
        # List all available ports for debugging
        print(f"Available MIDI ports: {ports}")
            
        selected_port = ports[0]  # Always use first port (X-Touch Mini)
        print(f"Connecting to X-Touch Mini: {selected_port}")
        
        # Try with default backend first (which should be available)
        try:
            print("Trying with default backend")
            # Don't explicitly set a backend, let mido choose the available one
            inport = mido.open_input(selected_port)
            print(f"Successfully connected to X-Touch Mini: {inport.name}")
            connected = True
            return True
        except Exception as backend_error:
            print(f"  Failed with default backend: {backend_error}")
            
            # If that fails, we can still try with explicit backends as before
            backends = ['mido.backends.rtmidi', 'mido.backends.portmidi']
            
            for backend in backends:
                try:
                    print(f"Trying with backend: {backend}")
                    mido.set_backend(backend)
                    inport = mido.open_input(selected_port)
                    print(f"Successfully connected to X-Touch Mini: {inport.name}")
                    connected = True
                    return True
                except Exception as backend_error:
                    print(f"  Failed with {backend}: {backend_error}")
            
        print("\nCould not connect to the X-Touch Mini with any available backend.")
        
        # Provide suggestions for troubleshooting
        print("\nTroubleshooting tips:")
        print("1. Make sure your X-Touch Mini is properly connected via USB")
        print("2. Check if you need to install X-Touch Mini drivers from Behringer's website")
        print("3. Try running the program as administrator")
        print("4. Check Windows Device Manager to see if the device is recognized")
        print("5. Ensure no other application is using the X-Touch Mini")
        
        return False
                
    except Exception as e:
        print(f"\nError connecting to X-Touch Mini: {e}")
        import traceback
        traceback.print_exc()
        return False

def disconnect_xtouch():
    """Disconnect from the X-Touch Mini controller"""
    global inport, connected
    
    if inport:
        try:
            print("Disconnecting from X-Touch Mini...")
            inport.close()
            inport = None
            connected = False
            print("X-Touch Mini disconnected")
            return True
        except Exception as e:
            print(f"Error disconnecting from X-Touch Mini: {e}")
    return False

def process_xtouch_messages():
    """Process messages from the X-Touch Mini controller"""
    global inport, connected, exit_flag, current_volume
    
    while not exit_flag:
        if not connected or not inport:
            time.sleep(0.1)
            continue
            
        try:
            for msg in inport.iter_pending():
                # Filter for controller 9 on channel 11 (0-indexed, so channel 10 in mido)
                # This is the volume slider on layer A of the X-Touch Mini
                if msg.type == 'control_change' and msg.channel == 10 and msg.control == 9:
                    print(f"Received: {msg}")
                    
                    # Direct mapping from X-Touch Mini value (0-127) to volume percentage (0-100%)
                    new_volume = msg.value / 127.0
                    
                    # Set the volume
                    volume.SetMasterVolumeLevelScalar(new_volume, None)
                    print(f"Volume set to: {new_volume * 100:.0f}%")
                    
                    # Update current volume reference
                    current_volume = new_volume
            time.sleep(0.001)  # Small sleep to prevent CPU hogging
        except Exception as e:
            print(f"Error processing X-Touch Mini messages: {e}")
            time.sleep(1)  # Wait before retrying

def handle_keyboard_shortcuts(e):
    """Handle keyboard shortcuts for connecting/disconnecting X-Touch Mini"""
    global connected
    
    # Ctrl+Page Down to release X-Touch Mini
    if keyboard.is_pressed('ctrl') and e.name == 'page down':
        if connected:
            print("Keyboard shortcut: Releasing X-Touch Mini")
            disconnect_xtouch()
    
    # Ctrl+Page Up to reconnect X-Touch Mini
    elif keyboard.is_pressed('ctrl') and e.name == 'page up':
        if not connected:
            print("Keyboard shortcut: Reconnecting X-Touch Mini")
            connect_xtouch()

def cleanup():
    """Cleanup function to release resources on exit"""
    global exit_flag, icon
    print("\nCleaning up resources...")
    exit_flag = True
    disconnect_xtouch()
    if icon:
        icon.stop()
    print("Cleanup complete. Goodbye!")

# Create a system tray icon
def create_image():
    """Create an image for the system tray icon"""
    width = 64
    height = 64
    color1 = (0, 0, 255)  # Blue
    color2 = (255, 255, 255)  # White
    
    image = Image.new('RGB', (width, height), color2)
    dc = ImageDraw.Draw(image)
    
    # Draw a simple volume icon
    speaker_width = width * 0.6
    speaker_height = height * 0.6
    
    # Draw speaker body
    speaker_x = width * 0.2
    speaker_y = height * 0.2
    
    # Base rectangle
    dc.rectangle(
        [(speaker_x, speaker_y + speaker_height * 0.25), 
         (speaker_x + speaker_width * 0.3, speaker_y + speaker_height * 0.75)],
        fill=color1
    )
    
    # Speaker cone
    points = [
        (speaker_x + speaker_width * 0.3, speaker_y + speaker_height * 0.15),  # Top left
        (speaker_x + speaker_width * 0.6, speaker_y),  # Top right
        (speaker_x + speaker_width * 0.6, speaker_y + speaker_height),  # Bottom right
        (speaker_x + speaker_width * 0.3, speaker_y + speaker_height * 0.85),  # Bottom left
    ]
    dc.polygon(points, fill=color1)
    
    # Sound waves
    for i in range(1, 4):
        center_x = speaker_x + speaker_width * 0.7
        center_y = speaker_y + speaker_height / 2
        radius = speaker_width * 0.1 * i
        
        dc.arc(
            [(center_x, center_y - radius), (center_x + radius * 2, center_y + radius)],
            start=270, end=90, fill=color1, width=2
        )
    
    return image

def setup_tray():
    """Set up the system tray icon and menu"""
    global icon
    
    # Create the icon image
    image = create_image()
    
    # Define the menu items
    menu = (
        pystray.MenuItem('Connected: ' + str(connected), lambda: None, enabled=False),
        pystray.MenuItem('Connect X-Touch Mini', connect_xtouch_from_tray),
        pystray.MenuItem('Disconnect X-Touch Mini', disconnect_xtouch_from_tray),
        pystray.MenuItem('Exit', exit_app)
    )
    
    # Create the icon
    icon = pystray.Icon("XTouchVolumeControl", image, "X-Touch Volume Control", menu)
    
    # Run the icon in a separate thread to avoid blocking
    # We need to make sure this thread can be properly stopped on exit
    icon_thread = threading.Thread(target=lambda: icon.run(), daemon=True)
    icon_thread.start()
    
    # Give the icon time to initialize
    time.sleep(0.5)

def connect_xtouch_from_tray(icon, item):
    """Connect to X-Touch Mini from the tray menu"""
    if not connected:
        connect_xtouch()
        update_connection_status()

def disconnect_xtouch_from_tray(icon, item):
    """Disconnect from X-Touch Mini from the tray menu"""
    if connected:
        disconnect_xtouch()
        update_connection_status()

def update_connection_status():
    """Update the connection status in the tray menu"""
    global icon, connected
    
    if icon:
        # Update the first menu item to show connection status
        icon.menu = (
            pystray.MenuItem('Connected: ' + str(connected), lambda: None, enabled=False),
            pystray.MenuItem('Connect X-Touch', connect_xtouch_from_tray),
            pystray.MenuItem('Disconnect X-Touch', disconnect_xtouch_from_tray),
            pystray.MenuItem('Exit', exit_app)
        )

def exit_app(icon, item):
    """Exit the application from the tray menu"""
    cleanup()
    os._exit(0)

# Register cleanup function to run on exit
atexit.register(cleanup)

# Main function
def main():
    global midi_thread, exit_flag
    
    try:
        # Set up system tray icon
        setup_tray()
        
        # Connect to X-Touch Mini on startup
        if not connect_xtouch():
            print("Failed to connect to X-Touch Mini on startup")
            print("You can try reconnecting with Ctrl+Page Up or from the tray menu")
        
        # Update connection status in tray menu
        update_connection_status()
        
        # Start monitoring keyboard shortcuts
        keyboard.on_release(handle_keyboard_shortcuts)
        
        # Start X-Touch Mini processing thread
        midi_thread = threading.Thread(target=process_xtouch_messages, daemon=True)
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

if __name__ == "__main__":
    main()