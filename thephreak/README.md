to connect to the badge:
goto esp-idf
. ./export.sh
run mpremote!

or use minicom or whatever to connect to the device.
https://opendev.org/openstack/etcd3gw


docker run -d -p 6379:6379 redislabs/redismod

Badge data sceheme to etcd:
badge / badge_id
badge / badge_id / nickname
badge / badge_id / matches
badge / badge_id / Intro / started = bool
badge / badge_id / Intro / completed = bool

badge / badge_id / challenge1 / 
badge / badge_id / challenge2 /
badge / badge_id / challenge3 / 
badge / badge_id / pvp /  




Game Flow:

On power up and network connection the badge needs to:
exchange cert with server. 

https API call to server/login - send UUID + Cert

Server checks if UUID exists in KVS
 if exists, server checks if cert is valid.
 if not, server registers UUID and cert
 returns a token for future calls with a ttl



On Init:
- Connect to Wifi
- Connect to Server to get current badge state
- set internal badge values. 

During the main loop of the badge:
- check wifi is connected to valid network 
    - if not:
        - start wifi connect routine
- check what challenge we're in
- if in Intro: 
    - Intro_routine()



Intro - at a set time OR event start command push a mqtt message to all badges to frenzy

Badges will report back 
