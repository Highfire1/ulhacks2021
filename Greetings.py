import discord
import os
import time
import discord.ext
from discord.utils import get
from discord.ext import commands, tasks

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send('Hello {0.name}~'.format(member))
        else:
            await ctx.send('Hello {0.name}... This feels familiar.'.format(member))
        self._last_member = member
    
    @commands.command()
    async def helpmath(self, ctx):
        """
        Sends messages to the central server!
        """
        channel = 876384651353137152

        ch = self.bot.get_channel(channel)
        text = f"`[{ctx.channel.id}, {ctx.message.id}]`\n"
        text += f"Question from `{ctx.author.name}` in `{ctx.guild.name}`:"
        text += "```" + ctx.message.content.replace("!helpmath ", "") + "```"

        sentmsg = await ch.send(text)

        await ctx.message.add_reaction("👍")

        return


        # below is defunct code
        '''
        def check(message):
            print("hello??")
            print(message.reference.jump_url)
            return False

        try:
            message = await self.bot.wait_for('on_message', check=check)
            
        except:
            print("timed out")
            # if wait_for times out
            pass
        else:
            print("reply!")
            # delete message if check is successful
            await sentmsg.channel.send("woah a reply")
        '''