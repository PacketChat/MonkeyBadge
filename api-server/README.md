# Api server for hushcon monkey badge

## execution
to run this either:
`python3 main.py`
or
`docker run api-server`

## turning on the intro game
POST to `/start_the_intro` with a json request body:
{
    key="ADMINSONLY"
}