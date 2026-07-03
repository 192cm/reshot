param(
  [string]$ProcessName = "NXTether",
  [int]$FocusDelayMilliseconds = 120
)

Add-Type @"
using System;
using System.Runtime.InteropServices;

public static class WindowFocusTools {
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

  [DllImport("user32.dll")]
  public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);

  [DllImport("user32.dll")]
  public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

  [DllImport("user32.dll")]
  public static extern bool IsWindowVisible(IntPtr hWnd);

  [DllImport("user32.dll")]
  public static extern IntPtr GetForegroundWindow();

  [DllImport("user32.dll")]
  public static extern bool SetForegroundWindow(IntPtr hWnd);

  [DllImport("user32.dll")]
  public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);

  public static IntPtr FirstVisibleWindowForProcess(uint targetProcessId) {
    IntPtr found = IntPtr.Zero;
    EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
      uint processId;
      GetWindowThreadProcessId(hWnd, out processId);
      if (processId == targetProcessId && IsWindowVisible(hWnd)) {
        found = hWnd;
        return false;
      }
      return true;
    }, IntPtr.Zero);
    return found;
  }
}
"@

$targetProcess = $null
$targetHandle = [IntPtr]::Zero
$processes = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
foreach ($candidate in $processes) {
  $handle = [WindowFocusTools]::FirstVisibleWindowForProcess([uint32]$candidate.Id)
  if ($handle -ne [IntPtr]::Zero) {
    $targetProcess = $candidate
    $targetHandle = $handle
    break
  }
}

if (-not $processes) {
  throw "Could not find NX Tether process '$ProcessName'. Open NX Tether before capturing."
}

if ($targetHandle -eq [IntPtr]::Zero) {
  $running = $processes | Select-Object ProcessName, Id, MainWindowHandle, MainWindowTitle | Format-Table -AutoSize | Out-String
  throw "NX Tether is running, but Windows reports no visible NX Tether camera window. Reopen or restore NX Tether, then try again. Running candidates: $running"
}

$previousHandle = [WindowFocusTools]::GetForegroundWindow()
$SW_RESTORE = 9

try {
  [WindowFocusTools]::ShowWindowAsync($targetHandle, $SW_RESTORE) | Out-Null
  Start-Sleep -Milliseconds 40
  [WindowFocusTools]::SetForegroundWindow($targetHandle) | Out-Null
  Start-Sleep -Milliseconds $FocusDelayMilliseconds

  $wsh = New-Object -ComObject WScript.Shell
  $wsh.SendKeys("^1")
  Start-Sleep -Milliseconds 80
}
finally {
  if ($previousHandle -ne [IntPtr]::Zero) {
    [WindowFocusTools]::SetForegroundWindow($previousHandle) | Out-Null
  }
}