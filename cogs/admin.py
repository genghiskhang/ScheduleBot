import discord
from discord.ext import commands
import time
import asyncio
import userinfodb as db

STARTING_MAX_COURSES = 5

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    Command [ADMIN]
    show_all_members

    Displays the name and user id
    of every member in the server
    """
    @commands.command()
    async def show_all_members(self, ctx):
        if ctx.author.guild_permissions.administrator:
            members = "\n".join([f"{member.name}#{member.discriminator} - {member.id} - is_bot:{member.bot}" for member in ctx.channel.guild.members])
            embed = discord.Embed(
                title="Members List",
                description=members,
                color=discord.Color.fuchsia()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("You do not have permissions to use this command")

    """
    Command [ADMIN]
    add_all_users

    Adds the info of all the current
    members to the database if not
    already in there
    """
    @commands.command()
    async def add_all_users(self, ctx):
        if ctx.author.guild_permissions.administrator:
            for member in ctx.channel.guild.members:
                if not member.bot:
                    user_info = {
                        "name":member.name,
                        "discriminator":member.discriminator,
                        "discord_id":member.id,
                        "max_courses":STARTING_MAX_COURSES
                    }
                    db.add_user(user_info)
            await ctx.send("All users added successfully")
        else:
            await ctx.send("You do not have permissions to use this command")

    """
    Command [ADMIN]
    update_max_courses

    Updates a user's max courses
    """
    @commands.command()
    async def update_max_courses(self, ctx, user:discord.Member):
        if ctx.author.guild_permissions.administrator:
            def user_check(m):
                return ctx.author == m.author

            try:
                await ctx.send(f"What do you want to set the new max courses to (>= {len(db.get_all_courses_info(user.id))})")
                msg = await self.bot.wait_for("message", check=user_check, timeout=30)

                if db.update_max_courses(user.id, int(msg.content)):
                    await ctx.send(f"{user.name}'s max courses set to {msg.content}")
                else:
                    await ctx.send("Please enter a valid max courses")
            except asyncio.TimeoutError:
                await ctx.send("Sorry, you did not reply in time")
        else:
            await ctx.send("You do not have permissions to use this command")

    """
    Command [ADMIN]
    wipe_user_messages_from

    Wipes all the messages sent by a
    user ina specific channel up to
    a certain amount
    """
    @commands.command()
    async def wipe_user_messages_from(self, ctx, user_id, channel_id, limit):
        if ctx.author.guild_permissions.administrator:
            try:
                await ctx.send("Start processing...")
                start_time = int(time.time())
                channel_name = ""
                for channel in ctx.guild.channels:
                    if channel.id == int(channel_id):
                        channel_name = channel.name

                user_message_id = []
                channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
                async for message in channel.history(limit=int(limit)):
                    if message.author.id == int(user_id):
                        user_message_id.append(message.id)
                processing_time = int(time.time() - start_time)
                await ctx.send(f"Finished processing {len(user_message_id)} of user's messages (Time: {int(processing_time / (60 * 60))}h {int((processing_time % (60 * 60)) / 60)}m {(processing_time % (60 * 60)) % 60}s)\nStart deletion...")

                for message_id in user_message_id:
                    try:
                        msg = await channel.fetch_message(message_id)
                        await msg.delete()
                    except:
                        pass
                end_time = int(time.time() - start_time)
                await ctx.send(f"Finished deletion (Time: {int(end_time / (60 * 60))}h {int((end_time % (60 * 60)) / 60)}m {(end_time % (60 * 60)) % 60}s)")
                await ctx.send(f"{len(user_message_id)} Messages Deleted ")
            except Exception as e:
                await ctx.send("Something went wrong...")
                await ctx.send(f"Error: {e}")
        else:
            await ctx.send("You do not have permissions to use this command")

async def setup(bot):
    await bot.add_cog(Admin(bot))