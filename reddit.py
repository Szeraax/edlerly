import praw
import json
import os
import dotenv

dotenv.load_dotenv()
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

config = json.load(open("config.json"))

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="Edler/1.0.0",
)

pledgethread = reddit.submission(config["pledge-thread"])

pledgethread.comments.replace_more(limit=0)

def findpledge(users):
    permalink = ""
    for user in users:
        for top_level_comment in pledgethread.comments:
            if top_level_comment.author == user:
                pledge = [f"https://reddit.com{top_level_comment.permalink}", user]
    if pledge[0] == "": raise Exception("Comment not found")
    else: return pledge
