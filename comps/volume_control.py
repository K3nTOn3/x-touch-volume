from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class VolumeControl:
    """Class to handle system volume control"""
    
    def __init__(self):
        # Set up volume control
        self.devices = AudioUtilities.GetSpeakers()
        interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Get current volume (value between 0.0 and 1.0)
        self.current_volume = self.volume.GetMasterVolumeLevelScalar()
        print(f"Current volume: {self.current_volume * 100:.0f}%")
        
    def get_volume(self):
        """Get the current system volume (0.0 to 1.0)"""
        return self.current_volume
        
    def set_volume(self, new_volume):
        """Set the system volume (0.0 to 1.0)"""
        self.volume.SetMasterVolumeLevelScalar(new_volume, None)
        self.current_volume = new_volume
        return self.current_volume
