# Reading .env file or asking for repository path

$dotenvPath = ".\.env"
if (Test-Path $dotenvPath) {
    Get-Content "$dotenvPath" `
        | Select-String -Pattern "^[^#]\w*" `
        | ForEach-Object {$_.ToString().Replace("`"", "")} `
        | ConvertFrom-String -Delimiter "=" -PropertyNames envvar, envvarvalue `
        | ForEach-Object {New-Variable -Name $_.envvar -Value $_.envvarvalue}
    Write-Host "Using $qgis_repo as qgis repo"
} else {
    Write-Host "You don't have .env file"
    $qgis_repo = Read-Host -Prompt 'Input the reporitory path:'
    $stream = [System.IO.StreamWriter] $dotenvPath
    $stream.WriteLine("qgis_repo=$qgis_repo")
    $stream.close()
}

$name = "Historisation"
$source = "..\$name"
$qgis_repo_conf = "$qgis_repo\sitnqgis.xml"
$destination = "$qgis_repo\$name"

# Deploy qgis plugin

if (Test-path "$destination.zip") {Remove-item "$destination.zip"}
if (Test-path $destination) {Remove-Item -Force -Recurse $destination}
# Get version from git tag and set it in metadata.txt
$newVersion = git describe --abbrev=0 --tags
(Get-Content $source\metadata.txt) -replace '^version=.+',"version=$newVersion" | Set-Content $source\metadata.txt
Copy-Item -Path $source -Recurse -Destination "$destination\$name" -Container
Add-Type -assembly "system.io.compression.filesystem"
[io.compression.zipfile]::CreateFromDirectory($destination, "$destination.zip")
Remove-Item -Force -Recurse $destination
git checkout $source\metadata.txt
# Update plugin metadata in repository
if (Test-path "$destination.zip") {
    [xml]$xml = Get-Content $qgis_repo_conf
    $element = $xml.SelectSingleNode("//pyqgis_plugin[@name='$name']")
    $OldVersion = $element.GetAttribute("version")
    $element.SetAttribute("version", $newVersion)
    $element = $xml.SelectSingleNode("//pyqgis_plugin[@name='$name']/update_date")
    $element.innerText = Get-Date -Format s
    $xml.Save($qgis_repo_conf)
    Write-Host "Version $newVersion of $name deployed. The old version was $OldVersion"
}

Remove-Variable qgis_repo
