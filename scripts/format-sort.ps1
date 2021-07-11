<#
.SYNOPSIS
Runs isort, autoflake, and black
Install required tools via "pip install autoflake isort black"
 #>
#>

# Sort imports one per line, so autoflake can remove unused imports
Set-Location "$PSScriptRoot/.."
& isort --atomic --force-single-line-imports .
& autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py
& isort --atomic .
& black .