import requests_oauthlib
from requests_oauthlib import OAuth2Session
from flask import Flask
from flask import request
from threading import Thread
import queue
import os
import dotenv
import json

config = json.load(open("config.json"))
baseurl = config["redirect-base-url"]

dotenv.load_dotenv()
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")

app = Flask(__name__)

connectionqueue = queue.Queue()
urlqueue = queue.Queue()

client_id = DISCORD_CLIENT_ID
client_secret = DISCORD_CLIENT_SECRET

scope = "connections"

oauth = OAuth2Session(client_id, scope=scope, redirect_uri="{baseurl}/api/Authorized")

def geturl():
    authorization_url, state = oauth.authorization_url("https://discord.com/oauth2/authorize")
    urlqueue.put(authorization_url)

def getreddit(connections):
    redditconnections = []
    redditaccounts = []
    for connection in connections:
        if connection["type"] == "reddit":
            redditconnections.append(connection)
    for connection in redditconnections:
        redditaccounts.append(connection["name"])
    return redditaccounts

@app.route("/api/Authorized", methods=["GET"])
def getcode():
    authorization_response = request.url
    token = oauth.fetch_token('https://discord.com/api/oauth2/token', authorization_response=authorization_response, client_secret=client_secret)
    connectionqueue.put(getreddit(oauth.get("https://discord.com/api/users/@me/connections").json()))
    return "<p>We are verifying your reddit account. You can close this tab.</p>"

def runserver():
    app.run(port=80, debug=False, host="0.0.0.0")

def startflask():
  t = Thread(target=runserver)
  t.start()
