$watchFolder = "C:\Python Projects\Automatic Attendance System\images\training\face"
$commandToRun = "python .\main.py --detection-type=folder_trigger"

# Get the initial file list
$fileList = Get-ChildItem -Path $watchFolder -Recurse -File | Where-Object { $_.Extension -match '\.(jpg|jpeg|png|gif)$' }

while ($true) {
    # Get the current file list
    $currentFileList = Get-ChildItem -Path $watchFolder -Recurse -File | Where-Object { $_.Extension -match '\.(jpg|jpeg|png|gif)$' }

    # Compare the current list with the previous list to find new files
    $newFiles = Compare-Object -ReferenceObject $fileList -DifferenceObject $currentFileList -Property FullName -PassThru

    # Run the command for each new file
    if ($newFiles) {
        foreach ($file in $newFiles) {
            Write-Host "New file added: $($file.FullName)"
            Invoke-Expression $commandToRun
        }
    }

    # Compare the previous list with the current list to find deleted files
    $deletedFiles = Compare-Object -ReferenceObject $currentFileList -DifferenceObject $fileList -Property FullName -PassThru

    # Run the command for each deleted file
    if ($deletedFiles) {
        foreach ($file in $deletedFiles) {
            Write-Host "File deleted: $($file.FullName)"
            # You can optionally run a command for file deletion here
        }
    }

    # Update the file list for the next iteration
    $fileList = $currentFileList

    Start-Sleep -Seconds 1
}
