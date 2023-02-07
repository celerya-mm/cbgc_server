#!/bin/bash
# per salire sul container e scegliere la cartella temporanea di salvataggio (eg tmp)
# docker exec -it postgres-db bash

# setup crontab per esecuzione script
# crontab -e
# 0 13 * * * /bin/bash share/Multimedia/05_Documenti/Flask/cbgc_server/backup_script.sh

# Define the maximum number of backups to keep
max_backups=14

# Define the path to the backup directory
backup_dir="share/Multimedia/BK_PostgresDB/bue_grasso_web"

# Count the number of backups in the directory
num_backups=$(find $backup_dir | wc -l)

# If the number of backups exceeds the maximum, delete the oldest
if [ "$num_backups" -gt $max_backups ]; then
  oldest_backup=$(find -t $backup_dir | tail -1)
  rm "$backup_dir/$oldest_backup"
fi

# print current folder
# sudo pwd

# Run the backup command inside container
sudo docker exec postgres-db pg_dump -U "postgres" -F t -f "tmp/dump.tar" bue_grasso_web

# copy from container and save in folder backup
sudo docker cp postgres-db:/tmp/dump.tar "$backup_dir/db_cbgc_$(date +%Y%m%d_%H%M).tar"
