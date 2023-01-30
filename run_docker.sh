echo killing old docker processes
docker-compose rm -fs

echo building docker containers

docker-compose rm -fs && docker-compose build --no-cache && docker-compose up
