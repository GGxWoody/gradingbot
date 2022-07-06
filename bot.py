import os

from dotenv import load_dotenv
from os.path import join
from twitchio.ext import commands

dir_path = os.path.dirname(os.path.realpath(__file__))
dotenv_path = join(dir_path, '.env')
load_dotenv(dotenv_path)

# credentials
TMI_TOKEN = os.environ.get('TMI_TOKEN')
CLIENT_ID = os.environ.get('CLIENT_ID')
BOT_NICK = os.environ.get('BOT_NICK')
BOT_PREFIX = os.environ.get('BOT_PREFIX')
CHANNEL = os.environ.get('CHANNEL')

bot = commands.Bot(
    irc_token=TMI_TOKEN,
    client_id=CLIENT_ID,
    nick=BOT_NICK,
    prefix=BOT_PREFIX,
    initial_channels=[CHANNEL]
)

Users = {}
isGradingActive = False


@bot.event
async def event_ready():
    """ Runs once the bot has established a connection with Twitch """
    print(f"{BOT_NICK} is online!")


@bot.event
async def event_message(ctx):
    if ctx.author.name.lower() == BOT_NICK.lower():
        return

    await bot.handle_commands(ctx)


@bot.command(name='start')
async def start_grade(ctx):
    if ctx.author.is_mod:
        global isGradingActive, Users
        Users = {}
        isGradingActive = True


@bot.command(name='stop')
async def stop_grade(ctx):
    global isGradingActive, Users
    if ctx.author.is_mod and len(Users) > 0:
        isGradingActive = False
        all_grades = 0
        for val in Users.values():
            all_grades += val
        new_maximum_val = max(Users.keys(), key=(lambda new_k: Users[new_k]))
        new_minimum_val = min(Users.keys(), key=(lambda new_k: Users[new_k]))
        await ctx.send(f'Score: {round(all_grades/len(Users),6)} Voters: {len(Users)} High: {Users[new_maximum_val]} ({new_maximum_val}), Low: {Users[new_minimum_val]}({new_minimum_val})')
    if ctx.author.is_mod and len(Users) == 0:
        isGradingActive = False
        await ctx.send(f'No votes')


@bot.command(name='last')
async def last_grade(ctx):
    global Users
    if ctx.author.is_mod and len(Users) > 0:
        all_grades = 0
        for val in Users.values():
            all_grades += val
        new_maximum_val = max(Users.keys(), key=(lambda new_k: Users[new_k]))
        new_minimum_val = min(Users.keys(), key=(lambda new_k: Users[new_k]))
        await ctx.send(
            f'Score: {round(all_grades / len(Users), 6)} Voters: {len(Users)} High: {Users[new_maximum_val]} ({new_maximum_val}) Low: {Users[new_minimum_val]} ({new_minimum_val})')
    if ctx.author.is_mod and len(Users) == 0:
        await ctx.send(f'No votes on previous grade')


@bot.command(name='score')
async def on_add(ctx):
    global isGradingActive, Users
    user = ctx.author.name
    if isGradingActive and ctx.author.name not in Users:
        command_string = ctx.message.content
        command_string = command_string.replace('!score', '').strip()
        try:
            value = float(command_string)
            value = round(value, 3)
        except ValueError:
            value = -1
        if 10 >= value >= 0:
            Users[user] = value
        else:
            ctx.send(f'@{user} Wrong score format')
    if ctx.author.name not in Users:
        ctx.send(f'@{user} Already graded')


if __name__ == "__main__":
    # launch bot
    bot.run()
