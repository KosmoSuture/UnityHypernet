# PowerShell Script to Replicate README Files from Sarah to All Other People
# This script copies Sarah's subfolder README files to John, Bridget, Mark, Richard, and Ollie
# with appropriate ID and name substitutions

Write-Host "=" * 80
Write-Host "README Replication Script for People Folders"
Write-Host "=" * 80
Write-Host ""

# Configuration
$basePath = "C:\Hypernet\Hypernet Structure\1 - People"
$sourcePerson = "1.2 Sarah Schaeffer"
$targetPeople = @(
    @{id="1.3"; name="John Schaeffer"; firstName="John"},
    @{id="1.4"; name="Bridget Schaeffer"; firstName="Bridget"},
    @{id="1.5"; name="Mark Schaeffer"; firstName="Mark"},
    @{id="1.6"; name="Richard Schaeffer"; firstName="Richard"},
    @{id="1.7"; name="Ollie Schaeffer"; firstName="Ollie"}
)

# Verify source path exists
$sarahPath = Join-Path $basePath $sourcePerson
if (-not (Test-Path $sarahPath)) {
    Write-Host "ERROR: Source path not found: $sarahPath" -ForegroundColor Red
    exit 1
}

Write-Host "Source: $sarahPath" -ForegroundColor Green
Write-Host ""

# Get all README files from Sarah's folder (excluding her main README)
$readmeFiles = Get-ChildItem -Path $sarahPath -Filter "README.md" -Recurse | Where-Object {
    $_.DirectoryName -ne $sarahPath
}

Write-Host "Found $($readmeFiles.Count) subfolder README files to replicate" -ForegroundColor Cyan
Write-Host ""

# Counter for created files
$totalCreated = 0
$totalSkipped = 0

# Process each person
foreach ($person in $targetPeople) {
    Write-Host "Processing: $($person.name) ($($person.id))" -ForegroundColor Yellow
    Write-Host ("-" * 80)

    $personCreated = 0

    foreach ($readme in $readmeFiles) {
        # Get relative path from Sarah's folder
        $relativePath = $readme.FullName.Substring($sarahPath.Length + 1)

        # Transform path for target person
        $newRelativePath = $relativePath -replace "1\.2", $person.id
        $targetFile = Join-Path $basePath "$($person.id) $($person.name)" $newRelativePath

        # Check if file already exists
        if (Test-Path $targetFile) {
            Write-Host "  [SKIP] $newRelativePath (already exists)" -ForegroundColor DarkGray
            $totalSkipped++
            continue
        }

        # Read and transform content
        $content = Get-Content $readme.FullName -Raw

        # Replace person ID (1.2 -> target ID)
        $newContent = $content -replace "1\.2", $person.id

        # Replace person name
        $newContent = $newContent -replace "Sarah Schaeffer", $person.name

        # Replace possessive forms
        $newContent = $newContent -replace "Sarah's", "$($person.firstName)'s"

        # Create directory if needed
        $targetDir = Split-Path $targetFile -Parent
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }

        # Write file
        try {
            Set-Content -Path $targetFile -Value $newContent -Force
            Write-Host "  [CREATE] $newRelativePath" -ForegroundColor Green
            $totalCreated++
            $personCreated++
        } catch {
            Write-Host "  [ERROR] Failed to create $newRelativePath : $_" -ForegroundColor Red
        }
    }

    Write-Host "  Created $personCreated files for $($person.name)" -ForegroundColor Cyan
    Write-Host ""
}

# Summary
Write-Host "=" * 80
Write-Host "Summary" -ForegroundColor Green
Write-Host "=" * 80
Write-Host "Total files created: $totalCreated" -ForegroundColor Green
Write-Host "Total files skipped: $totalSkipped" -ForegroundColor Yellow
Write-Host ""
Write-Host "All README files have been successfully replicated!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Review the created files to ensure correctness"
Write-Host "2. Customize any person-specific content as needed"
Write-Host "3. Commit changes to Git to make folders visible on GitHub"
Write-Host ""
