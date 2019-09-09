#!/usr/bin/python3
import asyncio
import discord
import re
import json
from utils import Database, ChannelNotFoundException
from downloader import download_file
import sys
import os

class MyClient(discord.Client):
    def __init__(self, **options):

        super().__init__(**options)
        self.database = options['database']
        self.mp3cache = options['mp3cache']

        self.configpath = options['configpath']
        cfg = json.load(open(self.configpath))
        self.guild_id = cfg['guild_id']
        self.rythm_channel_id = cfg['rythm_channel']
        self.bot_control_channel_id = cfg['bot_control_channel']
        self.admin_id = cfg['admin_id']
        self.guild = None
        self.bot_control_channel = None
        self.rythm_channel = None
        self.vchannel = None

        self.queue = []
        self.np = None

    async def on_ready(self):

        print('Logged as', self.user)

        self.guild = self.get_guild(self.guild_id)
        print(f'guild is {self.guild}')
        self.bot_control_channel = self.get_channel(self.bot_control_channel_id)
        self.rythm_channel = self.get_channel(self.rythm_channel_id)
        print(f'control channel is {self.bot_control_channel}')
        assert self.guild is not None
        assert self.bot_control_channel is not None
        assert self.rythm_channel is not None
        assert self.database is not None
        print('finished loading')


    async def send_msg(self, msg:str, channel=None):
        if channel is None:
            channel = self.bot_control_channel
        await channel.send(msg)

    async def process_command(self, command):
        instr, *l = command.content[1:].split(' ', 1)
        if instr in ['get', 'list', 'add', 'del', 'clear', 'dump', 'die', 'dbreload',
                     'vjoin', 'vleave', 'play', 'skip', 'stop', 'pause', 'resume', 'np',
                     'queue', 'clear_queue', 'dbpick']:
            attr = getattr(self, 'command_'+instr)
            try:
                await attr(command)

            except Exception as e:
                await self.send_msg(str(e))
                raise e



    async def command_dbreload(self, command):
        user = command.author.id
        if user==self.admin_id:
            self.database = Database(self.database.path)
            await self.send_msg(f'reloaded database')
            print('reloaded database')

    async def command_get(self, command):
        idx = int(command.content.split(' ')[1])
        await self.send_msg(f'database[{idx}] = {self.database[idx]}')

    async def command_list(self, command):
        await self.send_msg(f'{self.database}')

    async def command_add(self, command):
        r = command.content.split(' ', 1)[-1]
        link, name = r.split(' ', 1)
        rec = {"link":link, "name":name}
        self.database.add(rec)
        await self.send_msg(f'added {rec} to database')
        print(f'added {rec} to database')


    async def command_del(self, command):
        idx = int(command.content.split(' ')[1])
        del self.database[idx]
        await self.send_msg(f'deleted {idx}\'th element  from database')
        print(f'deleted {idx}\'th element  from database')

    async def command_clear(self, command):
        user = command.author.id
        if user==self.admin_id:
            #limited to 100 messages at once
            await self.bot_control_channel.purge()
            print('cleared up to 100 messages')

    async def command_dump(self, command):
        user = command.author.id
        if user==self.admin_id:
            self.database.store()
            json.dump(self.mp3cache, open(self.mp3cache['path'], 'w'))
            await self.send_msg(f'stored database')

    async def command_die(self, command):
        user = command.author.id
        if user==self.admin_id:
            await self.send_msg(f'Goodnight, sweet prince')
            await self.command_vleave(command)
            await self.close()
            await sys.exit(0)

    async def command_vjoin(self, command):

        user = command.author.id
        if user==self.admin_id:
            for item in self.guild.channels:
                if item.type==discord.ChannelType.voice and self.admin_id in list(map(lambda r: r.id, item.members)):
                    self.vchannel = await item.connect()
                    print(item)
                    return
            raise ChannelNotFoundException

    async def command_vleave(self, command):
        user = command.author.id
        if user==self.admin_id and self.vchannel is not None:
            await self.vchannel.disconnect()

    async def command_play(self, command): # >play N | play <url>
        if self.vchannel is None:
            await self.command_vjoin(command)
        idx = command.content.split(' ', 1)[-1]

        if re.match(r'>play -?\d+', command.content):
            idx = int(idx) - 1 # db is indiced from 1 by users
            command.content = f">play {self.database[idx]['link']}"
            await self.send_msg(f"playing {self.database[idx]['name']} from database")
            await self.command_play(command)
        else:
            await self.download_play(idx)

    async def command_skip(self, command):
        await self.command_stop(None)
        await self.download_play(None)

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

    async def command_queue(self, command):
        if self.queue:
            await self.send_msg(f'{self.queue}')
        else:
            await self.send_msg('queue is empty')

    async def command_queue_clear(self, command):
        self.queue = []
        await self.send_msg('queue is now empty')

    async def command_dbpick(self, command): # >dbpick Evangelion
        query = command.content.split(' ', 1)[-1]
        for row in self.database:
            if row['name']==query:
                await self.send_msg('found result!')
                command.content = f">play {row['link']}"
                await self.command_play(command)
                return
        await self.send_msg('sorry, nothing found')


    async def command_stop(self, command):
        if self.vchannel is not None and self.vchannel.is_playing():
            self.vchannel.stop()

    async def command_pause(self, command):
        if self.vchannel is not None and self.vchannel.is_playing():
            self.vchannel.pause()

    async def command_resume(self, command):
        if self.vchannel is not None and self.vchannel.is_paused():
            self.vchannel.resume()

    async def _precache(self, urls):
        for item in urls:
            await self.download_cached(item)

    async def download_cached(self, url):
        if url in self.mp3cache['data']:
            print(f"using cached record for {url}")
            return self.mp3cache['data'][url]
        else:
            filename = await download_file(url)
            self.mp3cache['data'][url] = filename
            return filename

    async def command_np(self, command):
        if self.np is None:
            await self.send_msg('nothing is playing')
        else:
            await self.send_msg(f'playing {self.np}')


    async def download_play(self, url=None):
        if url is not None:
            if self.vchannel is not None and self.vchannel.is_playing():

                self.queue.append(url)
                await self.send_msg(f'added {url} to the queue')
                await self._precache([url])
                return
            else:
                if self.vchannel is None:
                    mock = lambda r: 0 # create mock message
                    mock.author = lambda r: 0
                    mock.author.id = self.admin_id
                    await self.command_vjoin(mock)

                assert self.vchannel is not None
                filename = await self.download_cached(url)
                audio = discord.FFmpegPCMAudio(filename)
                self.vchannel.play(audio)
                self.np = url
                while self.vchannel.is_playing():
                    await asyncio.sleep(1)
                    #print(1)
                #print(2)
        self.np = None
        if self.queue:
            self.np = self.queue.pop()
            await self.download_play(self.np)




if __name__ == '__main__':
    configpath = './bot.json'
    data = './data.csv'
    mp3cache = './cache.json'
    if not os.path.exists(mp3cache):
        mp3cache = { "path":mp3cache, "data":{}}
    else:
        mp3cache = json.load(open(mp3cache))
    database = Database(database_path=data)
    client = MyClient(
        configpath=configpath,
        database=database,
        mp3cache=mp3cache
    )
    token = open('token.txt').read()
    client.run(token)
    print('ended')