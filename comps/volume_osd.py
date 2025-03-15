import tkinter as tk
from tkinter import ttk
import threading
import time

class VolumeOSD:
    """Class to display an on-screen volume indicator"""
    
    def __init__(self):
        self.window = None
        self.showing = False
        self.hide_timer = None
        self.duration = 1.5  # Seconds to display the OSD
        self.width = 300
        self.height = 50
        self.initialized = False
        self.tk_thread = None
        self.tk_queue = []  # Commands to run on tk thread
        self.tk_lock = threading.Lock()
        
    def initialize(self):
        """Initialize the OSD window (called once)"""
        if self.initialized:
            return
            
        # Start Tkinter in its own thread to avoid mainloop issues
        self.tk_thread = threading.Thread(target=self._tk_mainloop, daemon=True)
        self.tk_thread.start()
        
        # Wait for initialization to complete
        while not self.initialized:
            time.sleep(0.05)
    
    def _tk_mainloop(self):
        """Run Tkinter mainloop in separate thread"""
        self.window = tk.Tk()
        self.window.withdraw()  # Hide initially
        self.window.overrideredirect(True)  # Remove window decorations
        self.window.attributes("-topmost", True)  # Keep on top
        self.window.attributes("-alpha", 0.8)  # Semi-transparent
        
        # Position at bottom center of screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = (screen_width - self.width) // 2
        y_position = screen_height - self.height - 100  # 100px from bottom
        
        self.window.geometry(f"{self.width}x{self.height}+{x_position}+{y_position}")
        
        # Style and widgets
        self.frame = ttk.Frame(self.window)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Volume label
        self.volume_text = tk.StringVar()
        self.volume_label = ttk.Label(
            self.frame, 
            textvariable=self.volume_text,
            font=("Arial", 12, "bold")
        )
        self.volume_label.pack(side=tk.TOP, pady=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.frame, 
            orient=tk.HORIZONTAL, 
            length=self.width-20, 
            mode='determinate'
        )
        self.progress.pack(side=tk.BOTTOM, pady=5, padx=10, fill=tk.X)
        
        self.initialized = True
        
        # Process tk commands
        def check_queue():
            with self.tk_lock:
                while self.tk_queue:
                    func, args = self.tk_queue.pop(0)
                    try:
                        func(*args)
                    except Exception as e:
                        print(f"Error in tk command: {e}")
            self.window.after(50, check_queue)
            
        check_queue()
        self.window.mainloop()
    
    def _queue_tk_command(self, func, *args):
        """Add a command to be executed in the Tkinter thread"""
        if not self.initialized:
            return
            
        with self.tk_lock:
            self.tk_queue.append((func, args))
    
    def _do_show(self, volume_level):
        """Actually show the window (called in tk thread)"""
        percent = int(volume_level * 100)
        self.volume_text.set(f"Volume: {percent}%")
        self.progress['value'] = percent
        
        if not self.showing:
            self.window.deiconify()
            self.showing = True
            
        # Cancel existing hide timer if any
        if self.hide_timer is not None:
            self.window.after_cancel(self.hide_timer)
            
        # Set timer to hide after duration
        self.hide_timer = self.window.after(int(self.duration * 300), self._do_hide)
    
    def _do_hide(self):
        """Actually hide the window (called in tk thread)"""
        if self.showing:
            self.window.withdraw()
            self.showing = False
            self.hide_timer = None
    
    def _do_destroy(self):
        """Actually destroy the window (called in tk thread)"""
        if self.window:
            self.window.quit()
        
    def show_volume(self, volume_level):
        """Show the volume OSD with the given level (0.0 to 1.0)"""
        if not self.initialized:
            self.initialize()
            
        self._queue_tk_command(self._do_show, volume_level)
        
    def hide(self):
        """Hide the volume OSD"""
        if self.initialized:
            self._queue_tk_command(self._do_hide)
            
    def destroy(self):
        """Destroy the window when closing the application"""
        if self.initialized:
            try:
                self._queue_tk_command(self._do_destroy)
                # Give a short time for the command to execute
                time.sleep(0.1)
            except Exception as e:
                print(f"Error destroying volume OSD: {e}")
            finally:
                self.initialized = False
                self.showing = False
