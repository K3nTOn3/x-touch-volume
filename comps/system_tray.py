import pystray
from PIL import Image, ImageDraw
import threading
import time
import os

class SystemTray:
    """Class to handle the system tray icon and menu"""
    
    def __init__(self, connect_func, disconnect_func, exit_func):
        """Initialize with callback functions"""
        self.connect_func = connect_func
        self.disconnect_func = disconnect_func  
        self.exit_func = exit_func
        self.icon = None
        
    def create_image(self):
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
    
    def connect_xtouch_from_tray(self, icon, item):
        """Connect to X-Touch Mini from the tray menu"""
        self.connect_func()
        self.update_connection_status()

    def disconnect_xtouch_from_tray(self, icon, item):
        """Disconnect from X-Touch Mini from the tray menu"""
        self.disconnect_func()
        self.update_connection_status()
        
    def exit_app(self, icon, item):
        """Exit the application from the tray menu"""
        self.exit_func(icon)
        
    def update_connection_status(self, connected=False):
        """Update the connection status in the tray menu"""
        if self.icon:
            # Update the first menu item to show connection status
            self.icon.menu = (
                pystray.MenuItem('Connected: ' + str(connected), lambda: None, enabled=False),
                pystray.MenuItem('Connect X-Touch', self.connect_xtouch_from_tray),
                pystray.MenuItem('Disconnect X-Touch', self.disconnect_xtouch_from_tray),
                pystray.MenuItem('Exit', self.exit_app)
            )
        
    def setup(self, get_connection_status):
        """Set up the system tray icon and menu"""
        # Create the icon image
        image = self.create_image()
        
        # Define the menu items
        menu = (
            pystray.MenuItem('Connected: ' + str(get_connection_status()), lambda: None, enabled=False),
            pystray.MenuItem('Connect X-Touch Mini', self.connect_xtouch_from_tray),
            pystray.MenuItem('Disconnect X-Touch Mini', self.disconnect_xtouch_from_tray),
            pystray.MenuItem('Exit', self.exit_app)
        )
        
        # Create the icon
        self.icon = pystray.Icon("XTouchVolumeControl", image, "X-Touch Volume Control", menu)
        
        # Run the icon in a separate thread to avoid blocking
        # We need to make sure this thread can be properly stopped on exit
        icon_thread = threading.Thread(target=lambda: self.icon.run(), daemon=True)
        icon_thread.start()
        
        # Give the icon time to initialize
        time.sleep(0.5)
        
    def stop(self):
        """Stop the system tray icon"""
        if self.icon:
            try:
                self.icon.stop()
            except Exception as e:
                print(f"Error stopping icon: {e}")
