import mido
import time

# Global variables related to MIDI
inport = None
connected = False

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

def process_xtouch_messages(exit_flag, volume_control, volume_osd):
    """Process messages from the X-Touch Mini controller"""
    global inport, connected
    
    while not exit_flag():
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
                    volume_control.set_volume(new_volume)
                    print(f"Volume set to: {new_volume * 100:.0f}%")
                    
                    # Show volume OSD
                    if volume_osd:
                        volume_osd.show_volume(new_volume)
            time.sleep(0.001)  # Small sleep to prevent CPU hogging
        except Exception as e:
            print(f"Error processing X-Touch Mini messages: {e}")
            time.sleep(1)  # Wait before retrying
            
def get_connection_status():
    """Return the current connection status"""
    global connected
    return connected
