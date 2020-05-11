# aniguesser-discord
this repo contains code for the bot used on our discord server. (warning, code was written from scratch at 3 AM and has little to no comments) Currently the bot is able to play links and search youtube. Also, queue feature is implemented.
## setup
1. pip3 install -r requirements.txt
2. get discord token, put it in token.txt, add the bot to your server
3. configure config.py
4. get google api token, put it in youtube_api_key.txt (used for search)
5. get tenor token, put it in tenor_token.txt (optional, but >gif won't work)
6. python3 run.py