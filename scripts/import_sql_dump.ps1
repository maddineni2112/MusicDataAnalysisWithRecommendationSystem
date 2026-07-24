param(
  [Parameter(Mandatory=$true)]
  [string]$DumpPath
)

Write-Host "Offline SQL dump import scaffold for: $DumpPath"
Write-Host "Use database-native restore tools after reviewing source license and schema mapping."
