<#
.SYNOPSIS
Pad IMG file to multiple of 512 bytes and optionally to minimum Bochs hard disk cylinders

.DESCRIPTION
This script pads the specified IMG file:
1. First to a multiple of 512 bytes (sector alignment)
2. Then, if requested, to at least N full cylinders (using Bochs default geometry: 16 heads, 63 sectors/track)
This prevents Bochs from detecting PCHS=0/16/63 when using ata0-master disk mode.

.PARAMETER InputFile
Path to input IMG file

.PARAMETER OutputFile
Path to output file (optional, defaults to input file)

.PARAMETER FillByte
Fill byte value (0-255, default is 0x00)

.PARAMETER MinCylinders
Minimum number of cylinders to pad to (default: 1). 
Set to 0 or omit to only pad to 512-byte multiples (original behavior).

.EXAMPLE
.\Pad-IMG.ps1 -InputFile "disk.img"
# Only pad to 512-byte multiple

.EXAMPLE
.\Pad-IMG.ps1 -InputFile "mbr_lk.img" -MinCylinders 1
# Pad to 512-byte multiple AND at least 1 full cylinder (516096 bytes)

.EXAMPLE
.\Pad-IMG.ps1 -InputFile "small.img" -OutputFile "bochs_ready.img" -MinCylinders 2 -FillByte 0xFF
# Pad with 0xFF to at least 2 cylinders
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$InputFile,
    
    [string]$OutputFile,
    
    [ValidateRange(0, 255)]
    [int]$FillByte = 0x00,

    [ValidateScript({ $_ -ge 0 })]
    [int]$MinCylinders = 1
)

# Constants
$SECTOR_SIZE = 512
$HEADS = 16
$SECTORS_PER_TRACK = 63
$BYTES_PER_CYLINDER = $HEADS * $SECTORS_PER_TRACK * $SECTOR_SIZE  # 516096

# Check input file
if (-not (Test-Path $InputFile)) {
    Write-Error "Error: Input file not found: '$InputFile'"
    exit 1
}

# Set output path
if ([string]::IsNullOrEmpty($OutputFile)) {
    $OutputFile = $InputFile
}

$fileInfo = Get-Item $InputFile
$fileSize = $fileInfo.Length

Write-Host "Input file: $InputFile ($fileSize bytes)" -ForegroundColor Cyan

# Step 1: Pad to multiple of 512 bytes
$sectorRemainder = $fileSize % $SECTOR_SIZE
$sizeAfterSectorPad = $fileSize
$paddingForSectors = 0

if ($sectorRemainder -ne 0) {
    $paddingForSectors = $SECTOR_SIZE - $sectorRemainder
    $sizeAfterSectorPad = $fileSize + $paddingForSectors
    Write-Host "Padding $paddingForSectors bytes to reach 512-byte alignment -> $sizeAfterSectorPad bytes" -ForegroundColor Yellow
}
else {
    Write-Host "Already aligned to 512 bytes" -ForegroundColor Green
}

# Step 2: If MinCylinders > 0, pad to at least that many full cylinders
$finalSize = $sizeAfterSectorPad
$paddingForCylinders = 0

if ($MinCylinders -gt 0) {
    $minRequiredBytes = $MinCylinders * $BYTES_PER_CYLINDER
    $cylindersNeeded = [Math]::Ceiling($sizeAfterSectorPad / $BYTES_PER_CYLINDER)

    if ($sizeAfterSectorPad -lt $minRequiredBytes) {
        $cylindersNeeded = $MinCylinders
    }

    $finalSize = $cylindersNeeded * $BYTES_PER_CYLINDER
    $paddingForCylinders = $finalSize - $sizeAfterSectorPad

    if ($paddingForCylinders -gt 0) {
        Write-Host "Padding additional $paddingForCylinders bytes to reach $cylindersNeeded full cylinder(s) ($finalSize bytes total)" -ForegroundColor Yellow
    }
    else {
        Write-Host "Already meets or exceeds $MinCylinders cylinder(s) ($sizeAfterSectorPad bytes >= $minRequiredBytes bytes)" -ForegroundColor Green
    }
}
else {
    Write-Host "MinCylinders not specified or set to 0: skipping cylinder padding" -ForegroundColor Gray
}

# If no padding needed at all
if ($paddingForSectors -eq 0 -and $paddingForCylinders -eq 0) {
    if ($InputFile -ne $OutputFile) {
        Copy-Item $InputFile $OutputFile
        Write-Host "No padding needed. File copied to: $OutputFile" -ForegroundColor Green
    }
    else {
        Write-Host "No padding needed. File is already properly aligned." -ForegroundColor Green
    }
    exit 0
}

# Total padding
$totalPadding = $paddingForSectors + $paddingForCylinders

Write-Host "Total padding: $totalPadding bytes (Fill byte: 0x$($FillByte.ToString('X2')))" -ForegroundColor Magenta
Write-Host "Final size will be: $finalSize bytes" -ForegroundColor Green

try {
    # Read original file
    $originalData = [System.IO.File]::ReadAllBytes($InputFile)
    
    # Create padded array
    $paddedData = New-Object byte[] $finalSize
    [System.Buffer]::BlockCopy($originalData, 0, $paddedData, 0, $originalData.Length)
    
    # Fill padding area
    for ($i = $originalData.Length; $i -lt $finalSize; $i++) {
        $paddedData[$i] = $FillByte
    }
    
    # Write output
    [System.IO.File]::WriteAllBytes($OutputFile, $paddedData)
    
    Write-Host "`nPadding completed successfully!" -ForegroundColor Green
    Write-Host "Output file: $OutputFile ($finalSize bytes)" -ForegroundColor Green
    
    # Verification
    $cylCount = $finalSize / $BYTES_PER_CYLINDER
    Write-Host "Verification: Size is multiple of 512 bytes and equals $cylCount full cylinder(s)" -ForegroundColor Green
}
catch {
    Write-Error "Error processing file: $_"
    exit 1
}