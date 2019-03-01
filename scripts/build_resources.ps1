<#
.SYNOPSIS
Compiles all known resources.qrc to resources.py using QGIS's pyrcc4.
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

# Init Q4W environment, replicates o4w_env.bat
[Environment]::SetEnvironmentVariable("PATH", [string]::Join(";", @($path, "%WINDIR%\system32", "%WINDIR%", "%WINDIR%\system32\WBem")))
[Environment]::SetEnvironmentVariable("PYTHONPATH", $inst.InstallPath + "\apps\qgis-ltr\python")
[Environment]::SetEnvironmentVariable("PYTHONHOME", $inst.InstallPath + "\apps\Python27")
[Environment]::SetEnvironmentVariable("QT_PLUGIN_PATH", $inst.InstallPath + "\apps\qgis-ltr\qtplugins;" + $inst.InstallPath + "\apps\qt4\plugins")
[Environment]::SetEnvironmentVariable("O4W_QT_LIBRARIES", $inst.InstallPath + "\lib\")
[Environment]::SetEnvironmentVariable("O4W_QT_HEADERS", $inst.InstallPath + "\include\qt4")
[Environment]::SetEnvironmentVariable("O4W_QT_PREFIX", $inst.InstallPath + "\apps\qt4")
[Environment]::SetEnvironmentVariable("O4W_QT_PLUGINS", $inst.InstallPath + "\apps\qt4\plugins")
[Environment]::SetEnvironmentVariable("OSGEO4W_ROOT", $inst.InstallPath)

$RESOURCE_FILES=@(
	"../qkan/createunbeffl/resources.qrc"
	"../qkan/exportdyna/resources.qrc"
	"../qkan/importdyna/resources.qrc"
	"../qkan/linkflaechen/resources.qrc"
	"../qkan/tools/resources.qrc"
)

foreach ($element in $RESOURCE_FILES)
{
    $target_file = $element.Replace(".qrc", ".py")
    Write-Host "Building $element"

    & $PYTHON -m PyQt5.pyrcc_main -o $target_file $element
}
Pause-Exit(0)