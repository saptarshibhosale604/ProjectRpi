#!/bin/bash

# README.md
# sudo crontab -e

# set the backup directory path (edit this path as per your requirement)
file_dir="/home/ssbrpi"
backup_dir="/home/ssbrpi/Project/Rpi/Backup/BashFile"
file=".bashrc"
filePrefex="bashrc"
maxBackupFiles=3 # maximum number of backup files to keep

maxBackupFiles=$((maxBackupFiles + 1)) # increment to account for the current backup file
# create the backup directory if it does not exist
# mkdir -p "$file_dir"

# timestamp for the backup filename
timestamp=$(date +"%Y%m%d_%H%M%S")
echo "timestamp: $timestamp"

file_path="$file_dir/$file"
backup_file="$backup_dir/${filePrefex}_$timestamp.bak"

echo "file_path: $file_path"
echo "backup_file: $backup_file"

# create new backup with a timestamped filename
cp "$file_path" "$backup_file"
echo "backup created: $backup_file"

# remove all but the maxBackupFiles most recent backups
ls -1t $backup_dir/${filePrefex}_* | tail -n +$maxBackupFiles | xargs -i{} rm -- {}
# ls -1t "$backup_dir/backupFile_*" | tail -n +2 | xargs -i{} rm -- {}
# ls -1t "/home/ssbrpi/Project/Rpi/Background/Test/BackupDir/backupFile_*" | tail -n +2 | xargs -i{} rm -- {}
# ls -1t '/home/ssbrpi/Project/Rpi/Background/Test/BackupDir/backupFile_*' | tail -n +2 | xargs -i{} rm -- {}
# ls -1t /home/ssbrpi/Project/Rpi/Background/Test/BackupDir/backupFile_* | tail -n +2 | xargs -i{} rm -- {}

echo "Old backups removed"


