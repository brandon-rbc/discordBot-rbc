from discord.ext import commands
import lavalink

import discord
import re
import asyncio
from time import sleep
from discord import Embed
from discord import utils

url_rx = re.compile(r'https?://(?:www\.)?.+')

# run java -jar .\Lavalink.jar


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('localhost', 7000, 'testing', 'na', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)

    @commands.command(name='join')
    async def join(self, ctx):
        # print(type(self))
        if ctx.author.voice:
            vc = ctx.author.voice.channel
            player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
            # print(type(player))
            if not player.is_connected:
                player.store('channel', ctx.channel.id)
                await self.connect_to(ctx.guild.id, str(vc.id))
                # print('join command worked')
            else:
                raise commands.CommandInvokeError('Join a voice channel first, loser')

    @commands.command(name='play')
    async def play(self, ctx, *, query):
        try:
            player = self.bot.music.player_manager.get(ctx.guild.id)
            # await asyncio.sleep(.5)
            # await player.set_volume(200)
            if not url_rx.match(query):
                query = f'ytsearch:{query}'

            results = await player.node.get_tracks(query)

            if not results or not results['tracks']:
                return await ctx.send('nathan found')

            embed = discord.Embed(color=discord.Color.blurple())

            if results['loadType'] == 'PLAYLIST_LOADED':
                tracks = results['tracks']

                for track in tracks:
                    # Add all of the tracks from the playlist to the queue.
                    player.add(requester=ctx.author.id, track=track)

                embed.title = 'Playlist Has Been Queued!'
                embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} videos'
            else:
                track = results['tracks'][0]
                embed.title = 'Video Queued'
                embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

                track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
                player.add(requester=ctx.author.id, track=track)

            await ctx.send(embed=embed)

            if not player.is_connected:
                await self.join(ctx)

            if not player.is_playing:
                await asyncio.sleep(1)
                await player.play()
                # print(f'{player.queue}\n')

        except Exception as error:
            print(error)

    @commands.command(name='leave', aliases=['disconnect'])
    async def leave(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send('i am not even in a vc, dummy')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('you are not able to disconnect without being in the voice channel')

        player.queue.clear()
        await player.stop()
        await player.set_pause(False)
        await ctx.guild.change_voice_state(channel=None)
        await ctx.send('cy@')

    @commands.command(name='queue')
    async def queue(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        q = player.queue
        embed = discord.Embed(color=discord.Color.blurple(), title='Current Queue:')

        # embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
        queueList = ''
        index = 1
        if not q:
            embed.description = 'There are currently no queued videos :^('
        else:
            for video in q:
                queueList = queueList + f'{index}. {video.title} - {video.uri}\n\n'
                index = index + 1
            embed.description = queueList
        await ctx.send(embed=embed)

    @commands.command(name='pause')
    async def pause(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if player.paused:
            await ctx.send('I am already paused.')
        else:
            await player.set_pause(True)
            await ctx.send('Paused audio')

    @commands.command(name='unpause')
    async def unpause(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.paused:
            await ctx.send('I am already playing audio.')
        else:
            await player.set_pause(False)
            await ctx.send('Unpaused audio')

    @commands.command(name='skip', aliases=['next'])
    async def skip(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.queue:
            await ctx.send('There are no tracks to skip to')
            await ctx.send('Now leaving the vc')
            await self.leave(ctx)
        else:
            await player.skip()
            await ctx.send('skipped lol')

    @commands.command(name='remove')
    async def remove(self, ctx, *, track: int):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        # checking to see if the user entered a (valid) track to be removed from the queue
        if not track or not(0 < track < len(player.queue)):
            await ctx.send('Please enter a valid track number to remove from the queue. (*hint: use the ~queue command to look at currently queued videos*)')
        else:
            removedSong = player.queue[track-1]
            player.queue.remove(removedSong)
            await ctx.send(f'**{removedSong.title}** has been removed from the queue')



    @commands.command(name='volume')
    async def volume(self, ctx, *, vol: int):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if 0 <= vol <= 100:
            await asyncio.sleep(.5)
            await player.set_volume(vol)
            await ctx.send(f'Volume has been set to {vol}.')
        else:
            await ctx.send('Please choose an audio level between 0 and 100')

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            player = event.player
            t = 0  # timer
            while True:
                await asyncio.sleep(1)
                t = t + 1
                if player.is_playing:
                    print('bot no longer afk')
                    break
                if t == 60:
                    await self.connect_to(guild_id, None)
        elif isinstance(event, lavalink.events.TrackStartEvent):
            pass

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)


def setup(bot):
    bot.add_cog(MusicCog(bot))

