IMAGE=cbgc
TAG_NAME=$(IMAGE):latest
CONTAINER=cbgc-app

.PHONY:build
build:
docker=build . --force-rm -t @(TAG_NAME)

.PHONY:run
run:
    docker=run -d -p 8000:8000 -n @(CONTAINER) @(TAG_NAME)
    docker=image prune -f --filter 'dangling=true'

kill:
    @echo='Killing container...'
    @docker= docker ps  | grep @(container) | awk '{print $$1}' | xargs docker stop
