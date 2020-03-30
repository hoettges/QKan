<#
.SYNOPSIS
Compiles all known resources.qrc to resources.py using QGIS's pyrcc.
#>

$path = ""

function Pause-Exit($code)
{
    Write-Host 'Press Enter to exit.'
    [void][System.Console]::ReadKey($true)
    exit $code
}
if ($inst = Get-ItemProperty -Path "HKLM:\SOFTWARE\QGIS 3.10" -Name InstallPath -ErrorAction SilentlyContinue)
{
    $path = $inst.InstallPath
}
else
{
    $path = Read-Host -Prompt "Could not find installation path of QGIS 3.10.`nPlease enter it manually"
}

if ([string]::IsNullOrEmpty($path))
{
    Write-Error -Message "Empty path entered or found. Aborting."
    Pause-Exit(1)
}

Write-Host "Using '$path'"

$PYTHON = $path + "\bin\python-qgis-ltr.bat"

if (-not (Test-Path $PYTHON))
{
    Write-Error -Message "python-qgis-ltr.bat seems to be missing in your installation. Aborting."
    Pause-Exit(1)
}

$RESOURCE_FILES=@(
	"../qkan/createunbeffl/resources.qrc"
	"../qkan/exportdyna/resources.qrc"
	"../qkan/exporthe8/resources.qrc"
	"../qkan/importdyna/resources.qrc"
	"../qkan/linkflaechen/resources.qrc"
	"../qkan/xmlporter/resources.qrc"
	"../qkan/tools/resources.qrc"
)

foreach ($element in $RESOURCE_FILES)
{
    $target_file = $element.Replace(".qrc", ".py")
    Write-Host "Building $element"

    & $PYTHON -m PyQt5.pyrcc_main -o $target_file $element
}
Pause-Exit(0)