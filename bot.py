import os

from dotenv import load_dotenv
from os.path import join
from twitchio.ext import commands

dir_path = os.path.dirname(os.path.realpath(__file__))
dotenv_path = join(dir_path, '.env')
load_dotenv(dotenv_path)

# credentials
TOKEN = os.environ.get('TOKEN')
BOT_NICK = os.environ.get('BOT_NICK')
BOT_PREFIX = os.environ.get('BOT_PREFIX')
CHANNEL = os.environ.get('CHANNEL')


class Bot(commands.Bot):
    Users = {}
    isGradingActive = False

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=TOKEN, prefix=BOT_PREFIX, initial_channels=[CHANNEL])

    async def event_ready(self):
        """ Runs once the bot has established a connection with Twitch """
        print(f"{BOT_NICK} is online!")

    @commands.command(name='start')
    async def start_grade(self, ctx):
        if ctx.author.is_mod:
            global isGradingActive, Users
            Users = {}
            isGradingActive = True

    @commands.command(name='stop')
    async def stop_grade(self, ctx):
        global isGradingActive, Users
        if ctx.author.is_mod and len(Users) > 0 and isGradingActive:
            isGradingActive = False
            all_grades = 0
            for val in Users.values():
                all_grades += val
            new_maximum_val = max(Users.keys(), key=(lambda new_k: Users[new_k]))
            new_minimum_val = min(Users.keys(), key=(lambda new_k: Users[new_k]))
            await ctx.send(f'Score: {round(all_grades/len(Users),6)} Voters: {len(Users)} '
                           f'High: {Users[new_maximum_val]} ({new_maximum_val}) '
                           f'Low: {Users[new_minimum_val]}({new_minimum_val})')
        elif ctx.author.is_mod and len(Users) == 0:
            isGradingActive = False
            await ctx.send(f'No votes or no grading started')

    @commands.command(name='last')
    async def last_grade(self, ctx):
        global Users
        if ctx.author.is_mod and len(Users) > 0:
            all_grades = 0
            for val in Users.values():
                all_grades += val
            new_maximum_val = max(Users.keys(), key=(lambda new_k: Users[new_k]))
            new_minimum_val = min(Users.keys(), key=(lambda new_k: Users[new_k]))
            await ctx.send(f'Score: {round(all_grades / len(Users), 6)} Voters: {len(Users)} '
                           f'High: {Users[new_maximum_val]} ({new_maximum_val}) '
                           f'Low: {Users[new_minimum_val]} ({new_minimum_val})')
        if ctx.author.is_mod and len(Users) == 0:
            await ctx.send(f'No votes on previous grade')

    @commands.command(name='score')
    async def on_add(self, ctx):
        global isGradingActive, Users
        user = ctx.author.name
        print(ctx.message.content)
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
                print(f'{len(Users)} and user: {user} score added')


if __name__ == "__main__":
    bot = Bot()
    bot.run()
