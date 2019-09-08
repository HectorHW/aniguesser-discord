import discord

import json
from utils import Database
import sys



class MyClient(discord.Client):
    def __init__(self, **options):

        super().__init__(**options)
        self.database = options['database']

        self.configpath = options['configpath']

    async def on_ready(self):

        print('Logged as', self.user)
        cfg = json.load(open(configpath))
        self.guild_id = cfg['guild_id']
        self.rythm_channel_id = cfg['rythm_channel']
        self.bot_control_channel_id = cfg['bot_control_channel']
        self.admin_id = cfg['admin_id']
        self.guild = self.get_guild(self.guild_id)
        print(f'guild is {self.guild}')
        self.bot_control_channel = self.get_channel(self.bot_control_channel_id)
        print(f'control channel is {self.bot_control_channel}')
        assert self.guild is not None
        assert self.bot_control_channel is not None
        assert self.database is not None
        print('finished loading')


    async def send_msg(self, msg:str, channel=None):
        if channel is None:
            channel = self.bot_control_channel
        await channel.send(msg)



    async def process_command(self, command):
        instr, *l = command.content[1:].split(' ', 2)
        user = command.author.id
        try:
            if instr == 'get':
                idx = int(l[0])
                await self.send_msg(f'database[{idx}] = {self.database[idx]}')

            elif instr == 'list':
                await self.send_msg(f'{self.database}')

            elif instr == 'add':

                link, name = l[0], ' '.join(l[1:])
                rec = {"link":link, "name":name}
                self.database.add(rec)
                await self.send_msg(f'added {rec} to database')
                print(f'added {rec} to database')

            elif instr == 'del':
                idx = int(l[0])
                del self.database[idx]
                await self.send_msg(f'deleted {idx}\'th element  from database')
                print(f'deleted {idx}\'th element  from database')

            elif instr == 'clear':
                if user==self.admin_id:
                    #limited to 100 messages at once
                    await self.bot_control_channel.purge()
                    print('cleared up to 100 messages')

            elif instr == 'dump':
                if user==self.admin_id:
                    self.database.store()
                    await self.send_msg(f'stored database')

            elif instr == 'die':
                if user==self.admin_id:
                    await self.send_msg(f'Goodnight, sweet prince')
                    await self.close()
                    await sys.exit(0)


        except Exception as e:
            await self.send_msg(str(e))
            raise e




    async def on_message(self, message:discord.message.Message):
        # don't respond to myself and outside of control channel
        if message.author == self.user or message.channel.id!=self.bot_control_channel_id:
            return
        if message.content == 'Богдан':
            await message.channel.send('пидор')
        elif message.content == 'Вован':
            await message.channel.send('лучший!')
        elif message.content.startswith('>'):
            await self.process_command(message)





if __name__ == '__main__':
    configpath = './bot.json'
    data = './data.json'
    database = Database(database_path=data)
    client = MyClient(
        configpath=configpath,
        database=database
    )
    token = open('token.txt').read()
    client.run(token)
    print('ended')