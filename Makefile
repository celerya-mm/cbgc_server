IMAGE=cbgc
TAG_NAME=$(IMAGE):latest
CONTAINER=cbgc-service

.PHONY:build
build:
docker=build . --force-rm -t @(TAG_NAME)

.PHONY:run
run:
    docker=run -d -p 8000:5000 -n @(CONTAINER) @(TAG_NAME) --restart=always
    docker=image prune -f --filter 'dangling=true'

kill:
    @echo='Killing container...'
    @docker= docker ps  | grep @(container) | awk '{print $$1}' | xargs docker stop
