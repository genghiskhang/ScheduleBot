import discord
from discord.ext import commands
import re
import asyncio
from assets import userinfodb as db
from assets import botexceptions as be

STARTING_MAX_COURSES = 5

class Courses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    Event
    on_member_join

    Adds the info of the user that
    joined to the database
    """
    @commands.Cog.listener()
    async def on_member_join(self, member):
        user_info = {
            "name":member.name,
            "discriminator":member.discriminator,
            "discord_id":member.id,
            "max_courses":STARTING_MAX_COURSES
        }
        try:
            db.add_user(user_info)
        except be.UserExistsException as e:
            pass

    """
    Event
    on_member_update

    Updates the info of the user
    when they change their name
    or discriminator
    """
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        user_info = {
            "name":before.name,
            "discriminator":before.discriminator,
            "discord_id":before.id
        }
        db.update_user(user_info)

    """
    Event
    on_member_remove
    """
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        pass
        # db.remove_user(member.id)

    """
    Command
    show_courses

    Displays the all the courses
    a user has
    """
    @commands.command()
    async def show_courses(self, ctx):
        try:
            courses = [course_info["course_id"] for course_info in db.get_all_courses_info(ctx.author.id)]

            if not courses:
                raise be.NoCoursesException()

            embed = discord.Embed(
                title=f"{ctx.author.name}'s Schedule",
                color=discord.Color.blue()
            )
            for course_info in db.get_all_courses_info(ctx.author.id):
                embed.add_field(
                    name=f"[{course_info['section_id']}] {course_info['course_id']} - {course_info['course_name']} with {course_info['professor']}",
                    value=f"{course_info['days_of_week']}\n{course_info['time']} in {course_info['location']}",
                    inline=False
                )
            await ctx.author.send(embed=embed)
        except be.NoCoursesException as e:
            await ctx.send(str(e))

    """
    Command
    add_course

    Prompts the user for inputs
    about course info and adds the
    course to the database
    """
    @commands.command()
    async def add_course(self, ctx):
        try:
            if len(db.get_all_courses_info(ctx.author.id)) == db.get_max_courses(ctx.author.id):
                raise be.MaxCoursesReachedException()

            course_info = {
                "course_id":"",
                "course_name":"",
                "section_id":"",
                "days_of_week":"",
                "time":"",
                "location":"",
                "professor":""
            }

            def user_check(m):
                return ctx.author == m.author

            def course_id_check(m):
                return re.search("^[A-Z]{2,4}\d{3}$", m.content) is not None

            def section_id_check(m):
                return re.search("^\d+$", m.content) is not None

            def days_of_week_check(m):
                return re.search("^(MON)?(TUE)?(WED)?(THU)?(FRI)?$", m.content) is not None

            def time_check(m):
                return re.search("^(0?[1-9]|1[0-2]):[0-5][0-9][Aa|Pp][Mm]$", m.content) is not None

            try:
                # course_id
                await ctx.send("What is the course ID?\nXXXXNNN (i.e. CMSC202)")
                msg = await self.bot.wait_for("message", check=lambda m:course_id_check(m) and user_check(m), timeout=30)
                course_info["course_id"] = msg.content

                # course_name
                await ctx.send("What is the name of the course?")
                msg = await self.bot.wait_for("message", check=user_check, timeout=30)
                course_info["course_name"] = msg.content

                # section_id
                await ctx.send("What is the section ID?\nPositive numbers only")
                msg = await self.bot.wait_for("message", check=lambda m:section_id_check(m) and user_check(m), timeout=30)
                course_info["section_id"] = msg.content
                
                # days_of_week
                full_day = {
                    "MON":"Monday",
                    "TUE":"Tuesday",
                    "WED":"Wednesday",
                    "THU":"Thursday",
                    "FRI":"Friday"
                }
                await ctx.send("What days of the week do you have the course?\nEnter from [MON,TUE,WED,THU,FRI] no duplicates or spaces, in-order (i.e. MONWEDFRI)")
                msg = await self.bot.wait_for("message", check=lambda m:days_of_week_check(m) and user_check(m), timeout=30)
                course_info["days_of_week"] = ' '.join([full_day[j] for j in [msg.content[i:i + 3] for i in range(0, len(msg.content), 3)]])

                # time
                time = ""
                await ctx.send("What is the start time of the course?\nHH:MM(AM/PM) (i.e. 11:30AM)")
                msg = await self.bot.wait_for("message", check=lambda m:time_check(m) and user_check(m), timeout=30)
                time += msg.content + "-"
                await ctx.send("What is the end time of the course?\nHH:MM(AM/PM) (i.e. 11:30AM)")
                msg = await self.bot.wait_for("message", check=lambda m:time_check(m) and user_check(m), timeout=30)
                time += msg.content
                course_info["time"] = time.upper()

                # location
                await ctx.send("Where is the course located?")
                msg = await self.bot.wait_for("message", check=user_check, timeout=30)
                course_info["location"] = msg.content

                # professor
                await ctx.send("What is the name of the professor?")
                msg = await self.bot.wait_for("message", check=user_check, timeout=30)
                course_info["professor"] = msg.content

                db.add_course(ctx.author.id, course_info)
                await ctx.send("Course added successfully")
            except be.CourseExistsException as e:
                await ctx.send(str(e))
            except asyncio.TimeoutError:
                await ctx.send("Sorry, you did not reply in time")
        except be.MaxCoursesReachedException as e:
            await ctx.send(str(e))

    """
    Command
    remove_course

    Prompts the user to select the
    course they would like to remove
    """
    @commands.command()
    async def remove_course(self, ctx):
        try:
            courses = [course_info["course_id"] for course_info in db.get_all_courses_info(ctx.author.id)]

            if not courses:
                raise be.NoCoursesException()

            embed = discord.Embed(
                color=discord.Color.fuchsia()
            )
            embed.title = f"{ctx.author.name}, enter the course ID you want to remove"
            embed.description = "\n".join(courses)
            await ctx.send(embed=embed)

            def check(m):
                return m.content in courses and m.author == ctx.author

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30)
                db.remove_course(ctx.author.id, msg.content)
                await ctx.send(f"{msg.content} has been removed")
            except asyncio.TimeoutError:
                await ctx.send("Sorry, you did not reply in time")
        except be.NoCoursesException as e:
            await ctx.send(str(e))

    """
    Command
    update_course

    Prompts the user to select a course
    to update and what column of info
    they would like to update
    """
    @commands.command()
    async def update_course(self, ctx):
        try:
            courses = [course_info["course_id"] for course_info in db.get_all_courses_info(ctx.author.id)]
            schedule_columns = [column[0] for column in db.get_table_columns("schedules")]

            if not courses:
                raise be.NoCoursesException()

            def user_check(m):
                return m.author == ctx.author

            def course_id_check(m):
                return m.content in courses

            def column_check(m):
                return m.content in schedule_columns

            def column_value_check(m, column_name):
                if column_name == "course_id":
                    return re.search("^[A-Z]{2,4}\d{3}$", m.content) is not None
                elif column_name == "section_id":
                    return re.search("^\d+$", m.content) is not None
                elif column_name == "days_of_week":
                    return re.search("^(MON)?(TUE)?(WED)?(THU)?(FRI)?$", m.content) is not None
                elif column_name == "time":
                    return re.search("^(0?[1-9]|1[0-2]):[0-5][0-9][Aa|Pp][Mm]-(0?[1-9]|1[0-2]):[0-5][0-9][Aa|Pp][Mm]$", m.content) is not None
                else:
                    return True
            try:
                embed = discord.Embed(
                    title="Enter the course ID of the course you would like to edit",
                    description="\n".join(courses),
                    color=discord.Color.fuchsia()
                )
                await ctx.send(embed=embed)
                course_id = await self.bot.wait_for("message", check=lambda m:course_id_check(m) and user_check(m), timeout=30)
                
                embed = discord.Embed(
                    title="Which column would you like to update",
                    description="\n".join(schedule_columns),
                    color=discord.Color.fuchsia()
                )
                await ctx.send(embed=embed)
                column_name = await self.bot.wait_for("message", check=lambda m:column_check(m) and user_check(m), timeout=30)

                embed = discord.Embed(
                    title="What is the new column value",
                    description=f"Old column value: {db.get_all_courses_info(ctx.author.id)[courses.index(course_id.content)][column_name.content]}",
                    color=discord.Color.fuchsia()
                )
                if column_name.content == "course_id":
                    embed.description += "\n\nXXXXNNN (i.e. CMSC202)"
                elif column_name.content == "section_id":
                    embed.description += "\n\nPositive numbers only"
                elif column_name.content == "days_of_week":
                    embed.description += "\n\nSelect from [MON,TUE,WED,THU,FRI] (i.e. MONWEDFRI)"
                elif column_name.content == "time":
                    embed.description += "\n\nHH:MM(AM/PM)-HH:MM(AM/PM)"
                await ctx.send(embed=embed)
                column_value = await self.bot.wait_for("message", check=lambda m:column_value_check(m, column_name.content) and user_check(m), timeout=30)

                db.update_course(ctx.author.id, course_id.content, column_name.content, column_value.content)
                await ctx.send(f"Successfully updated the '{column_name.content}' column with the new value")
            except asyncio.TimeoutError:
                await ctx.send("Sorry, you did not reply in time")
        except be.NoCoursesException as e:
            await ctx.send(str(e))

    """
    view_user_courses

    Displays another user's courses
    """
    @commands.command()
    async def view_user_courses(self, ctx, user:discord.Member):
        try:
            courses = [course_info["course_id"] for course_info in db.get_all_courses_info(user.id)]

            if not courses:
                raise be.NoCoursesException()

            embed = discord.Embed(
                title=f"{user.name}'s Schedule",
                color=discord.Color.blue()
            )
            for course_info in db.get_all_courses_info(user.id):
                embed.add_field(
                    name=f"[{course_info['section_id']}] {course_info['course_id']} - {course_info['course_name']} with {course_info['professor']}",
                    value=f"{course_info['days_of_week']}\n{course_info['time']} in {course_info['location']}",
                    inline=False
                )
            await ctx.send(embed=embed)
        except be.NoCoursesException as e:
            await ctx.send(str(e))

async def setup(bot):
    await bot.add_cog(Courses(bot))