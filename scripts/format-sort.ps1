<#
.SYNOPSIS
Runs isort, autoflake, and black
Install required tools via "pip install autoflake isort black"
 #>
#>

# Sort imports one per line, so autoflake can remove unused imports
& isort --atomic --force-single-line-imports "$PSScriptRoot/.."
& autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place "$PSScriptRoot/.." --exclude=__init__.py
& isort --atomic "$PSScriptRoot/.."
& black "$PSScriptRoot/.."