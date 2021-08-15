import discord
import os
import time
import json
from sympy import N
from isoduration import parse_duration
import asyncio

import discord.ext
from discord.utils import get
from discord.ext import commands, tasks

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


from Greetings import Greetings # cog

from youtube import setup_google, youtube, youtube_video_info

# setup google authentication to use youtube api
# comment out to skip authentication
setup_google()

# bot setup
prefix = "!"
bot = commands.Bot(command_prefix=prefix)

# setup list of keywords that will call a youtube request
with open ("keywords.txt", "r") as f:
    keywords = f.readlines()
    keywords = [x.strip() for x in keywords] 

# nothing special

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="Math Tips", url="https://www.youtube.com/channel/UCCvI5slGo9QomdLRjHDHQ-A"))
    print("Everything's all ready to go~")

# overriding on_message to look for questions
@bot.event
async def on_message(message):

    # don't scan messages sent by bots
    if message.author.bot:
        return

    # just for debug
    print("new message:", message.content)

    # look for questions (yes its bad but it works in a demonstratable way lol)
    searchcontent = message.content.lower()

    if( "?" in searchcontent or 
        "what" in searchcontent or
        "how" in searchcontent or
        "help" in searchcontent
        ):
        for word in keywords:
            if word in searchcontent:
                #call youtube apis
                await keyword_found(message, word)
                return
    
    await check_helpchannel_reply(message)

    await bot.process_commands(message) # required to make other commands still work

# no theres no documentation here
async def check_helpchannel_reply(message):

    if message.reference != None:
        
        channel = await bot.fetch_channel(message.reference.channel_id)
        msg = await channel.fetch_message(message.reference.message_id)

        if msg.author.id == 876200253613809665:
            if "Question" in msg.content:

                
                print(msg.content)

                original_ch_id = msg.content[2:20]
                original_msg_id = msg.content[22:40]
                print(original_ch_id)
                print(original_msg_id)

                original_channel = await bot.fetch_channel(original_ch_id)
                original_msg = await original_channel.fetch_message(original_msg_id)

                response = f"From {message.author}:\n"
                response += f"```{message.content}```"

                await original_msg.reply(response)

                await message.add_reaction("👍")
                #originalmsg = await bot.fetch_message(originalid)

                #message.content[]
                #sender_channel 

# as alluded to, calls youtube apis
# and sends them to client
async def keyword_found(message, keyword):
    # generate message
    replymessage = "" 
    replymessage += f"Here are some useful videos on {keyword}!"

    # get "playlist" from youtube api
    query = youtube(keyword, count = 5)
    #print(query)

    # iterate through playlist
    for video in query["items"]:

        # ignore live streams
        if video["id"]["kind"] != "youtube#video":
            continue

        # call api again to get more video info
        video_info = youtube_video_info(video["id"]["videoId"])
        #print(video_info, "\n\n\n")
        
        # unload information from api call
        cur_vid = video_info["items"][0]

        vidlink = "https://www.youtube.com/watch?v=" + cur_vid["id"]
        vidname = cur_vid["snippet"]["title"]

        # do some finangling with the timestamp
        vidlength = cur_vid["contentDetails"]["duration"] # in iso 8601
        vidlength = parse_duration(vidlength) # now in proprietary format
        tmp = vidlength.time
        if tmp.hours != 0:
            vidlength = f"{tmp.hours}:{tmp.minutes}"
        else:
            vidlength = f"00:{tmp.minutes}"

        # add to message
        replymessage += f"\n`{vidname}` `{vidlength}` <{vidlink}>"

    # finally send message
    sentmsg = await message.reply(replymessage)
    await sentmsg.add_reaction("🗑️")

    #logic to delete message if trash can selected
    def check(reaction, user):
        return user == message.author and str(reaction.emoji) == "🗑️"

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except:
        # if wait_for times out
        await sentmsg.clear_reaction("🗑️") 
        # oh god if you delete this comment pyflakes thinks theres an error
    else:
        # delete message if check is successful
        await sentmsg.delete()

@bot.command()
async def ping(ctx):
    '''
    This text will be shown in the help command
    '''
    # Get the latency of the bot
    latency = bot.latency  # Included in the Discord.py library
    # Send it to the user
    await ctx.send(latency)


@bot.command()
async def echo(ctx, *, content:str):
    '''
    Echos some text, can probably be abused lol
    '''
    await ctx.send(content)

@bot.command()
async def e(ctx, *, content:str):
    '''
    Evaluates a math expression
    '''
    try:
        result = do_math(content)
        await ctx.reply(f"`{result}`")
    except:
        await ctx.reply("Sorry, something went wrong!")

# an unawaited function to do math outside the main thread
def do_math(content):
    result = N(content)
    if float(result).is_integer():
        result = int(result)
    return result
        
# ADD (unused) COG
bot.add_cog(Greetings(bot))

# below required if we want to load from cogs subfolder
#client.load_extension("main")


bot.run(os.environ['token'])


