# Monkey Badge

## badge
micropython code that runs on the badge.

## api-server
The api-server is the backend gameserver it provides an API interface for the badge to save state and complete challenges.

You will need a redis server with the json mod, `docker run -d -p 6379:6379 redislabs/redismod` works fine.

This is based on FastAPI and is easily executed with: `cd api-server; python3 api-server`

## scoreboard

Built with Flask
