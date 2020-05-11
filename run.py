#!/usr/bin/python3
import asyncio
import discord
import re
import json
from utils import ChannelNotFoundException
from downloader import download_file
import sys
import os
import config
from search import search, format_results

class MyClient(discord.Client):
    def __init__(self, **options):

        super().__init__(**options)
        self.mp3cache = options['mp3cache']
        self.guild_id = config.guild_id
        self.rythm_channel_id = config.rythm_channel_id
        self.bot_control_channel_id = config.bot_control_channel_id
        self.admin_id = config.admin_user_id
        self.guild = None
        self.bot_control_channel = None
        self.rythm_channel = None
        self.vchannel = None

        self.queue = []
        self.np = None

        self.commands = ['clear_chat', 'dump', 'die',
                         'vjoin', 'vleave', 'play', 'skip', 'stop', 'pause', 'resume', 'np',
                         'queue', 'clear', 'help',
                         'search', 'playfile', 's', 'p', 'q']

        self.search_results = None

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
        print('finished loading')


    async def send_msg(self, msg:str, channel=None):
        if channel is None:
            channel = self.bot_control_channel
        await channel.send(msg)

    async def process_command(self, command):
        instr, *l = command.content[1:].split(' ', 1)
        if instr in self.commands:
            attr = getattr(self, 'command_'+instr)
            try:
                await attr(command)

            except Exception as e:
                await self.send_msg(str(e))
                raise e

    async def command_search(self, command):  # >search evangelion op
        """
        >search <query>
        searches youtube for a video
        """
        query = command.content.split(' ', 1)[-1]
        results = search(query, 10)
        formatted = format_results(results)
        await self.send_msg(formatted)
        self.search_results = results

    async def command_s(self, command):
        """short for search - searches youtube for a video"""
        await self.command_search(command)

    async def command_help(self, message):
        """

        possible commands: list, add, del, clear, dump, die, dbrealod, play, skip, stop, pause, resume, np, queue, clear_queue
        """
        if message.content.lower()=='>help':
            await self.send_msg(self.command_help.__doc__)
        else:
            instr = message.content.split(' ', 1)[-1]
            if instr not in self.commands:
                await self.send_msg(f'excuse me wtf is {instr}')
                return
            attr = getattr(self, 'command_'+instr)
            await self.send_msg(attr.__doc__)


    async def command_clear_chat(self, command):
        user = command.author.id
        if user==self.admin_id:
            #limited to 100 messages at once
            await self.bot_control_channel.purge()
            print('cleared up to 100 messages')

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
            
            
    async def enqueue(self, url):
        await self.send_msg(f'added {url} to the queue')
        self.queue.append((url, await download_file(url)))


    async def play_link(self, url):
        """
        enqueue (and possibly start playing) given url
        """
        await self.enqueue(url)
        if self.vchannel is not None and not self.vchannel.is_playing():
            await self.play_from_queue()

    async def command_play(self, command): # >play <url>
        """
        play url (or enqueue it)
        """
        if self.vchannel is None:
            await self.command_vjoin(command)
        url:str = command.content.split()[-1]
        if 'youtube.com' in url or 'youtu.be' in url:
            await self.play_link(url)

    async def command_playfile(self, command):
        filename = command.content.split(' ', 1)[-1]

        user = command.author.id
        if not user==self.admin_id:
            return
        if filename.split('.')[-1] not in ['flac', 'mp3', 'wav']:
            await  self.send_msg('unsupported file format')
            return
        if self.vchannel is None:
            await self.command_vjoin(command)

        self.queue.append((filename, filename))

        if self.vchannel is not None and not self.vchannel.is_playing():
            await self.play_from_queue()


    async def command_p(self, command):
        """
        short for play
        """
        await self.command_play(command)


    async def play_from_queue(self):
        #time to play some music
        if not self.queue:
            return

        url, filename = self.queue.pop()
        audio = discord.FFmpegPCMAudio(filename)
        self.np = os.path.basename(filename).split(' --- ')[0]
        self.vchannel.play(audio)
        while self.vchannel.is_playing():
            await asyncio.sleep(1)
        self.np = None
        if self.queue:
            await self.play_from_queue()

    async def command_skip(self, _):
        """
        skips to next track
        """
        await self.command_stop(None)

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
        elif self.search_results is not None and re.match("\d+", message.content):
            num = int(message.content)-1
            if 0<=num<len(self.search_results):
                message.content = ">play "+"https://youtube.com"+self.search_results[num]['link']
                await self.command_play(message)
            self.search_results = None


    async def command_queue(self, _):
        """
        display queue
        """
        if self.queue:
            pretty = '\n'.join(['\n']+[f"""{i+1}. {os.path.basename(record[1]).split(" --- ")[0]}""" for i, record in enumerate(self.queue)])

            await self.send_msg(pretty)
        else:
            await self.send_msg('queue is empty')

    async def command_clear(self, _):
        """
        clears queue
        """
        self.queue.clear()
        await self.send_msg('cleared queue')

    async def command_q(self, _):
        """short for queue"""
        await self.command_queue(_)


    async def command_queue_clear(self, _):
        """
        clear queue
        """
        self.queue = []
        await self.send_msg('queue is now empty')


    async def command_stop(self, _):
        """
        DEPRECATED. use skip instead
        break playing. type play to start again from next record in queue
        """
        if self.vchannel is not None and self.vchannel.is_playing():
            self.vchannel.stop()

    async def command_pause(self, _):
        """
        pauses playing; also try resume
        """
        if self.vchannel is not None and self.vchannel.is_playing():
            self.vchannel.pause()

    async def command_resume(self, _):
        """
        resume playing after pausing
        """
        if self.vchannel is not None and self.vchannel.is_paused():
            self.vchannel.resume()


    async def command_np(self, _):
        """
        display currently playing track
        """
        if self.np is None:
            await self.send_msg('nothing is playing')
        else:
            await self.send_msg(f'playing {self.np}')






if __name__ == '__main__':
    configpath = './bot.json'
    data = './data.csv'
    mp3cache = './cache.json'
    if not os.path.exists(mp3cache):
        mp3cache = { "path":mp3cache, "data":{}}
    else:
        mp3cache = json.load(open(mp3cache))
    client = MyClient(
        configpath=configpath,
        mp3cache=mp3cache
    )
    token = open('token.txt').read()
    client.run(token)
    print('ended')