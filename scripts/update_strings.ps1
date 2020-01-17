<#
.SYNOPSIS
Collects all translation strings from .ui and .py files.
#>

$path = ""

function Pause-Exit($code)
{
    Write-Host 'Press Enter to exit.'
    [void][System.Console]::ReadKey($true)
    exit $code
}
if ($inst = Get-ItemProperty -Path "HKLM:\SOFTWARE\QGIS 3.4" -Name InstallPath -ErrorAction SilentlyContinue)
{
    $path = $inst.InstallPath
}
else
{
    $path = Read-Host -Prompt "Could not find installation path of QGIS 3.4.`nPlease enter it manually"
}

if ([string]::IsNullOrEmpty($path))
{
    Write-Error -Message "Empty path entered or found. Aborting."
    Pause-Exit(1)
}

Write-Host "Using '$path'"

$PYTHON = $path + "\bin\python-qgis.bat"

if (-not (Test-Path $PYTHON))
{
    Write-Error -Message "python-qgis.bat seems to be missing in your installation. Aborting."
    Pause-Exit(1)
}

$LOCALES=@("en")

foreach ($folder in Get-ChildItem -Path ..\qkan -Exclude __pycache__,doc,templates,test,i18n,.git -Directory)
{
    $plugin = $folder.BaseName
    Write-Host "Collecting translations for $plugin"
    
    $files=Get-ChildItem -Path $folder -Include *.py,*.ui -Recurse -File
    foreach ($locale in $LOCALES)
    {
        & $PYTHON -m PyQt5.pylupdate_main -noobsolete $files -ts "..\qkan\i18n\$($plugin)_$($locale).ts"
    }
}
Pause-Exit(0)