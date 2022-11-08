import json
import random
from re import search
import time
import asyncio
import discord
from discord.ext import commands
from discord_components import *
import DiscordUtils
import os
import youtube_dl
import wavelink
os.chdir(r"C:\Users\senti\Downloads\Advay Python\Number 1 Boi\ffmpeg\bin")

prefixes = {}
saves={}

def get_prefix(client, message):
    try:
        return prefixes[str(message.guild.id)]
    except KeyError:
        return ['?', ">"]

client = commands.Bot(command_prefix=(get_prefix), intents=discord.Intents.all())
music = DiscordUtils.Music()
timeRegex=r"([0-9]{1,2})[:ms](([0-9]{1,2})s?)?"

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.is_playing = False
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.lq=False
        self.autoplay=False
        self.vc=None
        self.player=None
        self.current_song=None
        self.pause_time=0
        self.delay_time=0
        self.place_queue=[]
        self.autoplay_queue=[]
        self.shuffled=True

    @commands.command(name="autoplay")
    async def _autoplay(self, ctx):
        self.autoplay=not self.autoplay
        try:
            self.current_song=music.get_player(guild_id=ctx.guild.id).current_queue()[0]
        except AttributeError:
            pass
        if self.autoplay:
            await ctx.send("Autoplay enabled!")
        else:
            await ctx.send("Autoplay disabled!")

    async def on_player_end(self, ctx):
        self.shuffled=False
        self.pause_time=0
        self.delay_time=0
        player=music.get_player(guild_id=ctx.guild.id)
        if self.lq:
                while True:
                    try:
                        await player.queue(self.current_song.url, search=True)
                        break
                    except KeyError:
                        continue
                print("hi")
                self.current_song=player.current_queue()[0]
                print(self.current_song.name)
                await asyncio.sleep(player.current_queue()[0].duration)
                await asyncio.sleep(self.delay_time)
                await self.on_player_end(ctx)
        elif self.autoplay:
            await self.doAutoplay(self.current_song, ctx)
        elif music.get_player(guild_id=ctx.guild.id).current_queue():
            while not ctx.voice_client.is_playing:
                pass
            print("hoi")
            await asyncio.sleep(music.get_player(guild_id=ctx.guild.id).current_queue()[0].duration)
            await asyncio.sleep(self.delay_time)
            await self.on_player_end(ctx)

    async def doAutoplay(self, nam, ctx):
        def searchYTbar(name):
            import urllib.request
            import re
            n = name.name.split(" ")
            try:
                html = urllib.request.urlopen("https://www.youtube.com/results?search_query={}".format(f"{'+'.join(name.channel.split(' '))}+{'+'.join(n)}"))
            except UnicodeEncodeError as e:
                print(n, e)
                return None
            video_ids = re.findall(
                r"watch\?v=(\S{11})", html.read().decode())
            print(video_ids)
            n=0
            while f"https://www.youtube.com/watch?v={video_ids[n]}" in self.autoplay_queue or f"https://www.youtube.com/watch?v={video_ids[n]}"==name.url:
                n+=1
            self.autoplay_queue.append(f"https://www.youtube.com/watch?v={video_ids[n]}")
            return f"https://www.youtube.com/watch?v={video_ids[n]}"
        self.skipped=False
        data=searchYTbar(nam)
        player = music.get_player(guild_id=ctx.guild.id)
        if not player.current_queue():
            while True:
                try:
                    await player.queue(data, search=True)
                    break
                except:
                    continue
            song = await player.play()
            self.current_song=song
            embed = (discord.Embed(title='Now playing',
                                   description=f"```css\n{song.title}\n```",
                                   color=discord.Color.blurple()).add_field(name='URL', value='[Click]({0.url})'.format(song)).set_thumbnail(url=song.thumbnail))
            await ctx.send(embed=embed)
            await asyncio.sleep(song.duration)
            await asyncio.sleep(self.delay_time)
            if song==self.current_song:
                await self.on_player_end(ctx)
                print(player.now_playing())
    @commands.command(name="save")
    async def _save(self, ctx, name: str):
        player=music.get_player(guild_id=ctx.guild.id)
        with open("allsaves.json", "r") as f:
            try:
                allsaves = json.load(f)
                for key in allsaves.keys():
                    saves[key] = allsaves[key]
            except Exception as e:
                print(e)
        if not player:
            return None
        if name not in list(saves.keys()):
            ls=[]
            for thing in player.current_queue():
                ls.append(str(thing.url))
            saves[name] = ls
            with open("allsaves.json", "w") as f:
                try:
                    json.dump(saves, f)
                except TypeError as e:
                    for thing in saves:
                        print(type(thing), [type(thin) for thin in saves[thing]])
                    print(e)
                    print(saves)
            string = '\n'.join([song.name for song in player.current_queue()])
            await ctx.send(f"Saved '{name}' as:\n{string}")
        else:
            await ctx.send(f"Sorry, '{name}' is already the name of a save.")
    
    @commands.command(name="load")
    async def _load(self, ctx, name: str):
        _player = music.get_player(guild_id=ctx.guild.id)
        with open("allsaves.json", "r") as f:
            allsaves = json.load(f)
            for key in allsaves.keys():
                saves[key] = allsaves[key]
        print(saves)
        if not _player:
            _player = music.create_player(ctx, ffmpeg_error_betterfix=True)
        if name in list(saves.keys()):
            async def _play_(ctx, player, song):
                if not ctx.voice_client.is_playing():
                    while True:
                        try:
                            await player.queue(song, search=True)
                            break
                        except KeyError:
                            continue
                    await player.play()
                else:
                    while True:
                        try:
                            await player.queue(song, search=True)
                            break
                        except KeyError:
                            continue
            for song in saves[name]:
                print(song)
                await _play_(ctx, _player, song)
            await asyncio.sleep(_player.current_queue()[0].duration)
            await asyncio.sleep(self.delay_time)
            await self.on_player_end(ctx)
        else:
            await ctx.send(f"'{name}' is not a save name.")
        
    @commands.command(name="restart")
    async def _restart(self, ctx):
        player=music.get_player(guild_id=ctx.guild.id)
        queue=player.current_queue()
        while player.current_queue():
            player.remove_from_queue(0)
        for song in queue:
            player.queue(song.url, search=True)
        await player.play()
        await asyncio.sleep(queue[0].duration)
        self.on_player_end(ctx)

    @commands.command(name="join")
    @commands.has_permissions(administrator=True)
    async def _join(self, ctx):
        voicetrue = ctx.author.voice
        if voicetrue is None:
            return await ctx.send('You have to be in a voice channel to use this command.')
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
            await ctx.send('Joined your voice channel \:)')
            self.vc = ctx.author.voice.channel
        else:
            await ctx.send('I am already in a different voice channel.')

    @commands.command(name="seek")
    async def _seek(self, ctx, time: int):
        player=music.get_player(guild_id=ctx.guild.id)
        await player.pause()
        await player.remove_from_queue(0)
        song=player.current_queue()[0]
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        ydl_opts = {'format': 'bestaudio'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song.url, download=False)
            URL = info['formats'][0]['url'] + "&t=10"
            print(info)
            voice = discord.utils.get(
                self.client.voice_clients, guild=ctx.guild)
            os.chdir(
                r"C:\Users\senti\Downloads\Advay Python\Number 1 Boi\ffmpeg\bin")
            voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        # url=f"{song.url}&t={time}"
        # queue=player.current_queue().copy()
        # while len(player.current_queue())>0:
        #     try:
        #         await player.remove_from_queue(0)
        #     except:
        #         break
        # print(queue, url)
        # for thing in queue:
        #     if thing==song:
        #         while True:
        #             try:
        #                 await player.queue(url)
        #                 break
        #             except Exception as e:
        #                 print(e)
        #                 continue
        #     else:
        #         while True:
        #             try:
        #                 await player.queue(thing.url, search=True)
        #                 break
        #             except Exception as e:
        #                 print(e)
        #                 continue
        # print("hi")
        # await player.play()

    @commands.command(name="leave")
    @commands.has_permissions(administrator=True)
    async def _leave(self, ctx):
        voicetrue = ctx.author.voice
        if voicetrue is None:
            return await ctx.send('You have to be in a voice channel to use this command.')
        await ctx.voice_client.disconnect()
        await ctx.send('Left your voice channel.')

    @commands.command(name="play", aliases=["p"])
    async def _play(self, ctx, *, video_link):
        self.skipped=False
        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            player = music.create_player(ctx, ffmpeg_error_betterfix=True)
        if ctx.voice_client is None:
            await self.vc.connect()
        if not ctx.voice_client.is_playing():
            while True:
                try:
                    await player.queue(video_link, search=True)
                    break
                except KeyError:
                    continue
            song=await player.play()
            self.current_song=song
            embed = (discord.Embed(title='Now playing',
                                   description=f"```css\n{song.title}\n```",
                                   color=discord.Color.blurple()).add_field(name='URL', value='[Click]({0.url})'.format(song)).set_thumbnail(url=song.thumbnail))
            await ctx.send(embed=embed)
            self.current_song = player.current_queue()[0]
            await asyncio.sleep(song.duration)
            await asyncio.sleep(self.delay_time)
            if self.current_song == song and not self.shuffled:
                await self.on_player_end(ctx)
        else:
            while True:
                try:
                    song= await player.queue(video_link, search=True)
                    break
                except KeyError:
                    continue
            await ctx.send(f"{song.name} has been added to the queue!")

    @commands.command(name="q", aliases=["queue"])
    async def _q(self, ctx):
        player = music.get_player(guild_id=ctx.guild.id)
        string = '\n'.join([song.name for song in player.current_queue()])
        embed=discord.Embed(title="Queue", description=string)
        await ctx.send(embed=embed)

    @commands.command(name="pause")
    @commands.has_permissions(administrator=True)
    async def _pause(self, ctx):
        try:
            player = music.get_player(guild_id=ctx.guild.id)
            await player.pause()
        except:
            pass
        if not player:
            await self.player.pause()
        await ctx.send('Paused.')
        self.is_playing = False
        self.pause_time=time.time()

    @commands.command(name="unpause", aliases=["resume"])
    @commands.has_permissions(administrator=True)
    async def _unpause(self, ctx):
        try:
            await music.get_player(guild_id=ctx.guild.id).resume()
        except:
            pass
        await ctx.channel.send('Unpaused.')
        self.is_playing = True
        if self.pause_time>0:
            self.delay_time+=time.time()-self.pause_time
    
    @commands.command(name="loop", aliases=['l'])
    async def _loop(self, ctx):
        player=music.get_player(guild_id=ctx.guild.id)
        song=await player.toggle_song_loop()
        if song.is_looping:
            return await ctx.send(f"{song.name} is now looping!")
        else:
            return await ctx.send(f"{song.name} is now not looping!")
    
    @commands.command(name="loopqueue", aliases=["lq"])
    async def _lq(self, ctx):
        self.lq = not self.lq
        if self.lq:
            player = music.get_player(guild_id=ctx.guild.id)
            self.place_queue = player.current_queue().copy()
            print(self.place_queue, player.current_queue())
            await ctx.send("Now looping queue!")
            # player = music.get_player(guild_id=ctx.guild.id)
            # queue=player.current_queue()
            # while True:
            #     if not self.lq:
            #         break
            #     if not player.current_queue:
            #         await player.stop()
            #         for thing in queue:
            #             while True:
            #                 try:
            #                     await player.queue(thing.url)
            #                     break
            #                 except KeyError:
            #                     continue
            #         await player.play()
            #         time.sleep(5)
        else:
            await ctx.send("Now not looping queue!")
    
    @commands.command(name="nowplaying", aliases=["np"])
    async def _np(self, ctx):
        player=music.get_player(guild_id=ctx.guild.id)
        song = player.now_playing()
        embed = (discord.Embed(title='Now playing',
                               description=f"```css\n{song.title}\n```",
                               color=discord.Color.blurple()).add_field(name='URL', value='[Click]({0.url})'.format(song)).set_thumbnail(url=song.thumbnail))
        await ctx.send(embed=embed)
    
    @commands.command(name="remove")
    async def _r(self, ctx, index):
        player=music.get_player(guild_id=ctx.guild.id)
        song = await player.remove_from_queue(int(index))
        await ctx.send(f"removed {song.name} from queue")
    
    @commands.command(name="skip")
    async def _s(self, ctx):
        player=music.get_player(guild_id=ctx.guild.id)
        song=await player.remove_from_queue(0)
        await ctx.send(f"skipped {song.name}")
        await self.on_player_end(ctx)

    @commands.command(name="skipto", aliases=["index"])
    async def _skipto(self, ctx, index: int):
        player = music.get_player(guild_id=ctx.guild.id)
        player.queue.position = index-2
    
    @commands.command(name="shuffle")
    async def _shuffle(self, ctx):
        self.shuffled=True
        player=music.get_player(guild_id=ctx.guild.id)
        ls=player.current_queue().copy()
        random.shuffle(ls)
        am = len(player.current_queue())
        for thing in range(am):
            try:
                await player.remove_from_queue(0)
            except IndexError:
                break
        #print(player.current_queue(), ls)
        await player.stop()
        player = music.create_player(ctx, ffmpeg_error_betterfix=True)
        for song in range(len(ls)):
            while True:
                try:
                    await player.queue(ls[song].url, search=True)
                    break
                except KeyError:
                    continue
        await player.play()
        string = '\n'.join([song.name for song in player.current_queue()])
        embed = discord.Embed(title="Queue", description=string)
        await ctx.send(embed=embed)
        await asyncio.sleep(player.current_queue()[0].duration)
        await self.on_player_end(ctx)

    @commands.command(name="stop")
    async def _stop(self, ctx):
        player=music.get_player(guild_id=ctx.guild.id)
        await player.stop()
        self.autoplay=False
        self.autoplay_queue.clear()
    
    @commands.command(name="volume", aliases=["vol", "v"])
    async def _v(self, ctx, amount: float):
        player=music.get_player(guild_id=ctx.guild.id)
        await player.change_volume(amount/100)
    
    @commands.command(name="eu4")
    async def _eu4(self, ctx):
        player = music.get_player(guild_id=ctx.guild.id)
        try:
            await player.stop()
        except:
            pass
        if not player:
            player = music.create_player(ctx, ffmpeg_error_betterfix=True)
        with open("saves.json", "r") as f:
            ls=json.load(f)
        random.shuffle(ls)
        for song in ls:
            while True:
                try:
                    await player.queue(song, search=True)
                    break
                except KeyError:
                    continue
        await player.play()
        self.player=player
        song = player.current_queue()[0]
        await asyncio.sleep(song.duration)
        if song == player.current_queue()[0]:
            if not self.shuffled:
                await self.on_player_end(ctx)

def setup(client):
    client.add_cog(Music(client))

@client.event
async def on_ready():
    setup(client=client)
    print("Ready")

client.run(token)
