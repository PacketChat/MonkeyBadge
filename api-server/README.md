# Api server for hushcon monkey badge

## execution
to run this either:

`python3 main.py`

or

`(docker | podman) run ghcr.io/packetchat/mb-api-server`

## turning on the intro game

POST to `/start_the_intro` with a json request body:

```json
{
    key="ADMINSONLY"
}
```
