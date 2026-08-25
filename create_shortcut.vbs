' Fallback shortcut creator, used when PowerShell is unavailable or locked
' down (Constrained Language Mode blocks New-Object -ComObject).
'
' Prints the shortcut path on success; exits non-zero on failure.

Option Explicit

Dim args, target, appScript, workDir, linkName
Dim shell, desktop, linkPath, link, fso

Set args = WScript.Arguments
If args.Count < 3 Then
    WScript.StdErr.WriteLine "usage: create_shortcut.vbs <target> <appScript> <workDir> [name]"
    WScript.Quit 1
End If

target = args(0)
appScript = args(1)
workDir = args(2)
If args.Count >= 4 Then
    linkName = args(3)
Else
    linkName = "Study Tracker"
End If

Set shell = CreateObject("WScript.Shell")

' SpecialFolders("Desktop") follows OneDrive's Known Folder Move, unlike
' %USERPROFILE%\Desktop which may not exist at all.
desktop = shell.SpecialFolders("Desktop")
If desktop = "" Then
    WScript.StdErr.WriteLine "Could not locate your Desktop folder."
    WScript.Quit 1
End If

linkPath = desktop & "\" & linkName & ".lnk"

On Error Resume Next
Set link = shell.CreateShortcut(linkPath)
link.TargetPath = target
link.Arguments = """" & appScript & """"
link.WorkingDirectory = workDir
link.Description = "Study Tracker - track your study hours"
link.IconLocation = target & ",0"
link.Save
If Err.Number <> 0 Then
    WScript.StdErr.WriteLine "Could not save the shortcut: " & Err.Description
    WScript.Quit 1
End If
On Error GoTo 0

Set fso = CreateObject("Scripting.FileSystemObject")
If fso.FileExists(linkPath) Then
    WScript.StdOut.WriteLine linkPath
    WScript.Quit 0
End If

WScript.StdErr.WriteLine "The shortcut did not appear at " & linkPath
WScript.Quit 1
