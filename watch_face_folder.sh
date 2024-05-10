#!/bin/bash

# Get the current working directory
CWD=$(pwd)

# Path to the folder you want to watch
WATCH_FOLDER="$CWD/images/training/face"

# Command to execute when new files are added
COMMAND_TO_RUN="python --version"

# Monitor the folder for new files
inotifywait -m -r -e create --format '%w%f' "$WATCH_FOLDER" |
while read FILE
do
    # Check if the newly added file is an image (you can adjust this condition based on your image file extensions)
    if [[ "$FILE" =~ \.(jpg|jpeg|png|gif)$ ]]; then
        echo "New image added: $FILE"
        # Run the Python script
        eval "$COMMAND_TO_RUN"
    else
        echo "Ignoring non-image file: $FILE"
    fi
done
