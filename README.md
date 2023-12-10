# Monkey Badge

This repository contains the hardware design files, badge code, and backend
infrastructure code for the HushCon Winter 2023 badge.

## badge

The code for the badge is based on [Micropython][1].  For full documentation
read the datasheet, comments, and commit history.

## api-server

The api-server is the backend gameserver it provides an API
interface for the badge to save state and complete challenges.

You will need a redis server with the json mod, `docker run -d -p 6379:6379
redislabs/redismod` works fine.

This is based on FastAPI and is easily executed with: `cd api-server; python3
api-server`

## scoreboard

Built, with Flask

<!--
vim: ts=2 sw=2 tw=80 syntax=md
!-->
