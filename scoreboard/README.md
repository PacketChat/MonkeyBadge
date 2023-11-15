# MonkeyBadge Scoreboard
## Usage
This is a flask app, install the requirements.txt contents via `pip` into your venv or container.
`pip3 install -r requirements.txt`
by default this runs in development mode on port 8080 with debug turned on.

A redis server with JSON needs to be accessible on localhost
`docker run -d -p 6379:6379 redislabs/redismod`

You can populate the redis server with synthetic badge data using the api-server/synthetic_badge_generator.py script. 
