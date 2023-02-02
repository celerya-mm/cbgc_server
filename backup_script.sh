#!/bin/bash

# Define the maximum number of backups to keep
max_backups=5

# Define the path to the backup directory
backup_dir="/backup"

# Count the number of backups in the directory
num_backups=$(ls $backup_dir | wc -l)

# If the number of backups exceeds the maximum, delete the oldest
if [ $num_backups -gt $max_backups ]; then
  oldest_backup=$(ls -t $backup_dir | tail -1)
  rm "$backup_dir/$oldest_backup"
fi

# Run the backup command
docker exec <container_name> pg_dump -F t -f "$backup_dir/db-$(date +%Y-%m-%d_%H-%M-%S).tar" <database_name>
