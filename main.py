import discord
from discord.ext import commands
import json
import discordoauth
import reddit
import os
import dotenv

dotenv.load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = commands.Bot(command_prefix="/", intents=intents)

config = json.load(open("config.json"))
battalions = config["battalions"]
forumname = config["interview-forum"]
battalionchoices = []

for i in battalions:
    battalionchoices.append(discord.app_commands.Choice(name=battalions[i]["name"], value=battalions[i]["name"]))

@client.tree.command(name="interview_get_battalions", description="Link to the current battalions list")
async def getbattalions(ctx: discord.interactions.Interaction):
    await ctx.response.send_message(embed=discord.Embed(title="View Battalion List", url="https://www.reddit.com/r/AprilKnights/comments/taccao/battalion_overview_thread", color=discord.Color.from_str("#c60c30")))
    

@client.tree.command(name="gatewatch_assign_battalion")
@discord.app_commands.choices(battalion=battalionchoices)
async def assignbattalion(ctx: discord.interactions.Interaction, target:discord.Member, battalion: discord.app_commands.Choice[str]):
    battalion = battalions[battalion.value]
    try:
        battalionrole = discord.utils.get(ctx.guild.roles, name=battalion["role-name"])
        await target.add_roles(battalionrole, atomic=True)
        battalionchannel = discord.utils.get(ctx.guild.channels, name=battalion["channel-name"])
        await battalionchannel.send(f"Please welcome the newest member of our battalion, {target.mention}!")
        await ctx.response.send_message(embed=discord.Embed(title="Successfully added member to battalion!", description=f"**Member:** {target.mention}\n**Battalion:** {battalion['name']}", color=discord.Color.from_str("#0fb309")))
    except Exception:
        await ctx.response.send_message("An error occured!")

@client.tree.command(name="gatewatch_discuss_candidate")
async def discusscandidate(ctx: discord.interactions.Interaction, target:discord.Member):
    forum = discord.utils.get(ctx.guild.forums, name=forumname)
    await forum.create_thread(content=f"From: <#{ctx.channel.id}>", name=f"{ctx.channel.name[-4:]}: {target.name}")
    await ctx.response.send_message(embed=discord.Embed(title="Successfully made discussion thread!", description=f"**Candidate:** {target.mention}", color=discord.Color.from_str("#0fb309")), ephemeral=True)

@client.tree.command(name="interview_verify_reddit")
async def verifyreddit(ctx: discord.interactions.Interaction):
    discordoauth.geturl()
    discordurl = discordoauth.urlqueue.get()
    await ctx.response.send_message(f"Please connect to your discord account here for verification: {discordurl}")
    redditconnections = discordoauth.connectionqueue.get()
    try:
        pledge = reddit.findpledge(redditconnections)
        await ctx.channel.send(embed=discord.Embed(title="Successfully found candidate's pledge!", description=f"**Reddit Username:** u/{pledge[1]}\n**Pledge:**\n{pledge[0]}", color=discord.Color.from_str("#0fb309")))
    except Exception:
        await ctx.channel.send("Pledge not found!")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online)
    await client.tree.sync()
    print(f'We have logged in as {client.user}')

def start(): 
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    discordoauth.startflask()
    start()