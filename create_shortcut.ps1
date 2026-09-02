<#
    Creates the "Study Tracker" Desktop shortcut.

    Kept as its own file rather than a -Command one-liner inside setup.bat so
    that paths containing spaces, ampersands or apostrophes don't have to
    survive two layers of quoting.

    Prints the shortcut path on success; exits non-zero on failure.
#>
# Deliberately not Mandatory: a missing value would make PowerShell prompt,
# which would hang setup.bat waiting on input it can never supply.
param(
    [string] $Target,
    [string] $AppScript,
    [string] $WorkDir,
    [string] $Name = "Study Tracker"
)

$ErrorActionPreference = "Stop"

if (-not $Target -or -not $AppScript -or -not $WorkDir) {
    [Console]::Error.WriteLine("usage: create_shortcut.ps1 -Target <exe> -AppScript <py> -WorkDir <dir>")
    exit 1
}

function Get-DesktopPath {
    # %USERPROFILE%\Desktop is NOT reliable: OneDrive's "Known Folder Move"
    # relocates the Desktop (usually to %OneDrive%\Desktop) and the old path
    # then does not exist at all. Ask Windows where it actually is, and only
    # fall back to guessing.
    $candidates = New-Object System.Collections.Generic.List[string]

    foreach ($folder in @("DesktopDirectory", "Desktop")) {
        try {
            $p = [Environment]::GetFolderPath($folder)
            if ($p) { $candidates.Add($p) }
        } catch { }
    }

    try {
        $key = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        $raw = (Get-ItemProperty -Path $key -Name "Desktop").Desktop
        if ($raw) { $candidates.Add([Environment]::ExpandEnvironmentVariables($raw)) }
    } catch { }

    foreach ($var in @($env:OneDrive, $env:OneDriveConsumer, $env:OneDriveCommercial)) {
        if ($var) { $candidates.Add((Join-Path $var "Desktop")) }
    }
    if ($env:USERPROFILE) { $candidates.Add((Join-Path $env:USERPROFILE "Desktop")) }

    foreach ($c in $candidates) {
        if (-not [string]::IsNullOrWhiteSpace($c) -and
            (Test-Path -LiteralPath $c -PathType Container)) {
            return $c
        }
    }
    return $null
}

$desktop = Get-DesktopPath
if (-not $desktop) {
    [Console]::Error.WriteLine("Could not locate your Desktop folder.")
    exit 1
}

$linkPath = Join-Path $desktop ($Name + ".lnk")

try {
    $shell = New-Object -ComObject WScript.Shell
    $link = $shell.CreateShortcut($linkPath)
    $link.TargetPath = $Target
    $link.Arguments = '"' + $AppScript + '"'
    $link.WorkingDirectory = $WorkDir
    $link.Description = "Study Tracker - track your study hours"
    $link.IconLocation = "$Target,0"
    $link.Save()
} catch {
    [Console]::Error.WriteLine("Could not save the shortcut: " + $_.Exception.Message)
    exit 1
}

if (Test-Path -LiteralPath $linkPath) {
    # [Console]::Out rather than Write-Output: the formatting pipeline wraps
    # long lines at the console width, which would split a long path.
    [Console]::Out.WriteLine($linkPath)
    exit 0
}

[Console]::Error.WriteLine("The shortcut did not appear at $linkPath")
exit 1
