echo killing old docker processes
docker-compose rm -fs

echo building docker containers
docker-compose build --force-rm --pull && docker-compose up
