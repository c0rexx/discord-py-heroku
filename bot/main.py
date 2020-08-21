import os
import io
import json
import random
import asyncio
import discord
import datetime
import requests
import wikipedia
import youtube_dl
import googletrans
import emoji_locale
from bs4 import BeautifulSoup
from discord.ext import commands
from google.cloud import vision
from google.oauth2 import service_account
from googleapiclient.discovery import build

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
GOOGLE_CLOUD_CREDENTIALS = service_account.Credentials.from_service_account_info(json.loads(os.getenv('GOOGLE_CLIENT_SECRETS')))
YOUTUBE_API_TOKEN = os.getenv('YOUTUBE_API_TOKEN')

bot = commands.Bot(command_prefix='p.')

basic_emoji = {
    'Si' : '<:Si:523966164704034837>',
    'Sadge' : '<:Sadge:696437945392955453>',
    'Pepega' : '<:Pepega:739020602194657330>',
    'forsenSmug' : '<:forsenSmug:736973361283858442>',
    'forsenScoots' : '<:forsenScoots:736973346142552195>',
    'forsenT' : '<:forsenT:743128058545832048>',
    'docSpin' : '<a:docSpin:743133871889055774>',
    'hackerCD' : '<a:hackerCD:744835324827402250>'
}
scoots_emoji = [
    '<:forsenScoots:736973346142552195>',
    '<:OMGScoots:736973384570634321>'
]
dance_emoji = [
    '<a:forsenPls:741611256460476496>',
    '<a:forsenDiscoSnake:742013168234135664>',
    '<a:headBang:742013167890333802>',
    '<a:KKool:742013168196517899>' + ' <a:GuitarTime:742013167554789390>',
    '<a:pepeJAM:742013167671967805>',
    '<a:AlienPls:742014131305054239>',
    '<a:SHUNGITE:744474032698556477> ' + '<a:doctorDance:744473646298431510>' + ' <a:SHUNGITE:744474032698556477>'
]
dance_react = [
    '<a:forsenPls:741611256460476496>',
    '<a:forsenDiscoSnake:742013168234135664>',
    '<a:headBang:742013167890333802>',
    '<a:KKool:742013168196517899>',
    '<a:pepeJAM:742013167671967805>',
    '<a:AlienPls:742014131305054239>',
    '<a:doctorDance:744473646298431510>'
]

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

activites = [
    discord.Game(name='with křemík.'),
    discord.Activity(type=discord.ActivityType.listening, name='frequencies.'),
    discord.Activity(type=discord.ActivityType.watching, name='you.')
    ]

async def status_changer():
    while True:
        await bot.change_presence(activity=random.choice(activites))
        await asyncio.sleep(30)

async def wait_until_release():
    x = datetime.datetime.utcnow()
    y = x.replace(day=x.day, hour=5, minute=7)
    if not (x.hour < 5 or (x.hour == 5 and x.minute < 7)):
        y += datetime.timedelta(days=1)
    delta_t = y - x
    await asyncio.sleep(delta_t.total_seconds())
    while True:
        await garf_comic(bot.guilds[0].text_channels[0], datetime.datetime.utcnow())
        await asyncio.sleep(86400)

@bot.event
async def on_ready():
    bot.loop.create_task(status_changer())
    bot.loop.create_task(wait_until_release())

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction(basic_emoji.get('Si'))
        await ctx.send(basic_emoji.get('Pepega') + '📣' + ' COMMAND NOT FOUND')
        return
    elif isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.message.add_reaction(basic_emoji.get('Si'))
        await ctx.send('Not available in DMs.')
        print(ctx.message.author.name + ' sent forbidden command DM request.')
        return
    raise error
    
def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)

def time_until_tomorrow():
    dt = datetime.datetime.utcnow()
    tomorrow = dt + datetime.timedelta(days=1)
    return datetime.datetime.combine(tomorrow, datetime.time.min) - dt + datetime.timedelta(hours=5, minutes=7)

def format_date(date):
    return str(str(date.year)+'/'+str(date.month).zfill(2)+'/'+str(date.day).zfill(2))

async def garf_comic(channel, date):
    link = 'Something went wrong.'
    url = 'http://www.gocomics.com/garfield/' + format_date(date)
    status = await channel.send(basic_emoji.get('hackerCD') + 'Sending HTTP request... ' + basic_emoji.get('docSpin'))
    response = None
    try:
        response = requests.get(url, headers)
        response.raise_for_status()
    except:
        fail = await channel.send('Bad response from ' + url + '.')
        await status.delete()
        await fail.add_reaction(basic_emoji.get('Si'))
        return
    await status.edit(content='Parsing ' + str(round((len(response.content)/1024.0),2)) + 'kB... ' + basic_emoji.get('docSpin'))
    soup = BeautifulSoup(response.content, 'html.parser')
    await status.edit(content='Looking for Garfield comic...')
    picture = soup.find_all('picture', attrs={'class': 'item-comic-image'})
    if not picture or not picture[0]:
        fail = await channel.send('Garfield comic not found on ' + url + '.')
        await status.delete()
        await fail.add_reaction(basic_emoji.get('Si'))
        return
    await status.edit(content='Garfield comic found.')
    link = picture[0].img['src']
    await status.delete()
    await channel.send(link)

@bot.command(name='roll', help='Generate a random number between 1 and 100 by default.')
async def roll(ctx, input: str = '100'):
    result = "No, I don't think so. " + basic_emoji.get('forsenSmug')
    if input.isnumeric():
        result = str(random.randint(1, int(input)))
    else:
        await ctx.message.add_reaction(basic_emoji.get('Si'))
    await ctx.send(result)

@bot.command(name='today', help="Get today's Garfield comic.")
async def today(ctx):
    now = datetime.datetime.utcnow()
    if now.hour < 5 or (now.hour==5 and now.minute < 7):
        release = datetime.datetime(now.year, now.month, now.day, 5, 7, 0, 0)
        td = (release - now)
        hours = td.seconds // 3600 % 24
        minutes = td.seconds // 60 % 60
        seconds = td.seconds - hours*3600 - minutes*60
        await ctx.send("You will have to be patient, today's comic comes out in " + str(hours).zfill(2) + ':' + str(minutes).zfill(2) + ':' + str(seconds).zfill(2) + '.')
    else:
        await garf_comic(ctx.channel, now)

@bot.command(name='yesterday', help="Get yesterdays's Garfield comic.")
async def yesterday(ctx):
    now = datetime.datetime.utcnow()
    await garf_comic(ctx.channel, now - datetime.timedelta(days=1))

@bot.command(name='tomorrow', help="Get tomorrow's Garfield comic? Unless??")
async def tomorrow(ctx):
    td = time_until_tomorrow()
    hours = td.seconds // 3600 % 24
    now = datetime.datetime.utcnow()
    minutes = td.seconds // 60 % 60
    seconds = td.seconds - hours*3600 - minutes*60
    if now.hour < 5 or (now.hour==5 and now.minute < 7):
        hours += 24
    response = "You will have to be patient, tomorrow's comic comes out in " + str(hours).zfill(2) + ':' + str(minutes).zfill(2) + ':' + str(seconds).zfill(2) + '.'
    await ctx.message.add_reaction(basic_emoji.get('Si'))
    await ctx.send(response)

# Adds 'st', 'nd', 'rd' to numbers
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')
# Formats datetime using above function
def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

@bot.command(name='random', help='Get random Garfield comic.')
async def rand_date(ctx):
    first = datetime.date(1978, 6, 19)
    now = datetime.datetime.utcnow()
    last = datetime.date(now.year, now.month, now.day)
    rd = random_date(first, last)
    await garf_comic(ctx.channel, rd)
    facts = None
    status = await ctx.send('Looking up an interesting fact... ' + basic_emoji.get('docSpin'))
    fact = ''
    wiki_success = True
    try:
        fact = wikipedia.page(rd.strftime('%B') + ' ' + str(rd.day)).section('Events')
        await status.edit(content='Searching wikipedia.com/wiki/' + rd.strftime('%B') + '_' + str(rd.day) + ' for an interesting fact.')
        facts = fact.splitlines()
    except:
        wiki_success = False
    if not wiki_success:
        await status.delete()
        fact = await ctx.send("Couldn't access wikipedia entry. " + basic_emoji.get('Sadge') + '\nThis comic came out in ' + custom_strftime('%B {S}, %Y', rd) + '.')
    elif not facts:
        await status.delete()
        fact = await ctx.send("Didn't find any interesting fact on wikipedia.com/wiki/" + rd.strftime('%B') + '_' + str(rd.day) + ". Probably retarded formatting on this page for the 'events' section." + sad_emoji )
    else:
        await status.delete()
        fact = await ctx.send('This comic came out in ' + custom_strftime('%B {S}, %Y', rd) + '. On this day also in the year ' + random.choice(facts))
        await fact.add_reaction(random.choice(scoots_emoji))

@bot.command(name='garf', help="Get specific Garfield comic, format: 'Year Month Day'.")
async def garf(ctx, arg1: str = '', arg2: str = '', arg3: str = ''):
    result = "No, I don't think so. " + basic_emoji.get('forsenSmug')
    if not arg1 or not arg2 or not arg3:
        result = "Date looks like 'Year Month Day', ie. '2001 9 11' :)."
        await ctx.message.add_reaction(basic_emoji.get('Si'))
    elif not arg1.isnumeric() or not arg2.isnumeric() or not arg3.isnumeric():
        result = "That's not even a numeric date."
        await ctx.message.add_reaction(basic_emoji.get('Si'))
    else:
        a1 = int(arg1)
        a2 = int(arg2)
        a3 = int(arg3)
        correctDate = None
        newDate = None
        now = datetime.date.today()
        try:
            newDate = datetime.date(a1,a2,a3)
            correctDate = True
        except ValueError:
            correctDate = False
        if not correctDate:
            result = 'No..? You must be using the wrong calendar.'
            await ctx.message.add_reaction(basic_emoji.get('Si'))
        elif newDate > now:
            result = 'You will have to wait for that day to come.'
            await ctx.message.add_reaction(basic_emoji.get('Si'))
        elif newDate >= datetime.date(1978, 6, 19):
            result = ''
            await garf_comic(ctx.channel, datetime.date(a1, a2, a3))
        else:
            result = "Unfortunately, Garfield didn't exist before 19th June 1978."
            await ctx.message.add_reaction(basic_emoji.get('Si'))
    if result:
        await ctx.send(result)

# WideHard - from https://github.com/Toaster192/rubbergod/blob/master/cogs/weather.py
@bot.command(name='weather', help="Get location's weather.")
async def weather(ctx, *args):
    city = 'Prague'
    if args:
        city = ' '.join(str(i) for i in args)
    url = ('http://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=en&appid=' + WEATHER_TOKEN)
    res = requests.get(url).json()
    if str(res['cod']) == '200':
        description = 'Weather in ' + res['name'] + ', ' + res['sys']['country']
        embed = discord.Embed(title='Weather', description=description)
        image = 'http://openweathermap.org/img/w/' + res['weather'][0]['icon'] + '.png'
        embed.set_thumbnail(url=image)
        weather = res['weather'][0]['main'] + ' (' + res['weather'][0]['description'] + ') '
        temp = str(res['main']['temp']) + '°C'
        feels_temp = str(res['main']['feels_like']) + '°C'
        humidity = str(res['main']['humidity']) + '%'
        wind = str(res['wind']['speed']) + 'm/s'
        clouds = str(res['clouds']['all']) + '%'
        visibility = str(res['visibility'] / 1000) + ' km' if 'visibility' in res else 'no data'
        embed.add_field(name='Weather', value=weather, inline=False)
        embed.add_field(name='Temperature', value=temp, inline=True)
        embed.add_field(name='Feels like', value=feels_temp, inline=True)
        embed.add_field(name='Humidity', value=humidity, inline=True)
        embed.add_field(name='Wind', value=wind, inline=True)
        embed.add_field(name='Clouds', value=clouds, inline=True)
        embed.add_field(name='Visibility', value=visibility, inline=True)
        await ctx.send(embed=embed)
    elif str(res['cod']) == '404':
        msg = await ctx.send('City not found.')
        await msg.add_reaction(basic_emoji.get('Sadge'))
    elif str(res['cod']) == '401':
        msg = await ctx.send('API key broke, have a nice day.')
        await msg.add_reaction(basic_emoji.get('Si'))
    else:
        await ctx.send('City not found! ' + basic_emoji.get('Sadge') + ' (' + res['message'] + ')')

@bot.command(name='fact', help="Get random fact about a day.")
async def fact(ctx, arg1: str = '', arg2: str = ''):
    date = None
    msg = ''
    if not arg1 or not arg2:
        date = datetime.datetime.today()
        msg = 'On this day in the year '
    elif not arg1.isnumeric() or not arg2.isnumeric():
        await ctx.send("That's not even a numeric date. Try 'Month Day'.")
        await ctx.message.add_reaction(basic_emoji.get('Si'))
        return
    else:
        a1 = int(arg1)
        a2 = int(arg2)
        correctDate = None
        now = datetime.date.today()
        try:
            date = datetime.date(2000,a1,a2)
            msg = 'On ' + custom_strftime('%B {S}', date) + ' in the year '
            correctDate = True
        except ValueError:
            correctDate = False
        if not correctDate:
            await ctx.send("No..? You must be using the wrong calendar. Try 'Month Day'.")
            await ctx.message.add_reaction(basic_emoji.get('Si'))
            return

    facts = None
    status = await ctx.send('Looking up an interesting fact...')
    fact = ''
    wiki_success = True
    try:
        fact = wikipedia.page(date.strftime('%B') + ' ' + str(date.day)).section('Events')
        await status.edit(content='Searching wikipedia.com/wiki/' + date.strftime('%B') + '_' + str(date.day) + ' for an interesting fact.')
        facts = fact.splitlines()
    except:
        wiki_success = False
    if not wiki_success:
        await status.delete()
        fact = await ctx.send("Couldn't access wikipedia entry " + basic_emoji.get('Sadge'))
    elif not facts:
        await status.delete()
        fact = await ctx.send("Didn't find any interesting fact on wikipedia.com/wiki/" + date.strftime('%B') + '_' + str(date.day) + ". Probably retarded formatting on this page for the 'events' section." + sad_emoji )
    else:
        await status.delete()
        fact = await ctx.send(msg + random.choice(facts))
        await fact.add_reaction(random.choice(scoots_emoji))

# Uses Google Cloud VisionAI
google_vision = vision.ImageAnnotatorClient(credentials=GOOGLE_CLOUD_CREDENTIALS)
def detect_text(url):
    # Download image from url
    response = requests.get(url)
    image = None
    try:
        # Convert data to image
        image_bytes = io.BytesIO(response.content)
        image = vision.types.Image(content=image_bytes.read())
    except:
        return "That's not an image? " + basic_emoji.get('Pepega') + '\n' + basic_emoji.get('forsenSmug')
    
    # Let VisionAI do its thing
    cloud_response = google_vision.text_detection(image=image)
    texts = cloud_response.text_annotations
    # Couldn't read anything
    if not texts:
        return "Can't see shit! " + basic_emoji.get('forsenT')
    # Else format text (max. 2000 characters)
    else:
        return '```' + texts[0].description[:1994] + '```'

@bot.command(name='read', help='Read image.')
@commands.guild_only()
async def read(ctx, url: str = ''):
    # Check whether user provided url or embedded image
    if not url and not ctx.message.attachments:
        await ctx.send("Read what? " + basic_emoji.get('Pepega') + '\n' + basic_emoji.get('forsenSmug'))
        await ctx.message.add_reaction(basic_emoji.get('Si'))
        return
    # Get url to the image
    if not url:
        url = ctx.message.attachments[0].url
    
    # Display status
    status = await ctx.send('Processing... ' + basic_emoji.get('docSpin'))
    # Attempt to detect text
    text = detect_text(url)
    await status.delete()
    await ctx.send(text)
    
translator = googletrans.Translator()
@bot.command(name='translate', help="Translate text.")
@commands.guild_only()
async def translate(ctx, *args):
    # No text entered -> nothing to translate
    if not args:
        await ctx.send("Translate what? " + basic_emoji.get('Pepega') + '\n' + basic_emoji.get('forsenSmug'))
        await ctx.message.add_reaction(basic_emoji.get('Si'))
        return
    
    result = None
    # Combine tuple into one long string
    arg = ' '.join(str(i) for i in args)
    # Get first word
    input = arg.split(' ', 1)
    # If it's an ISO639-1 language code, translate to that language
    if input[0] in googletrans.LANGUAGES:
        result = translator.translate(input[1], dest=input[0])
    # Otherwise translate to english by default
    else:
        result = translator.translate(arg, dest='en')
        
    # Debug
    print("Source lang: " + result.src + "\nDest lang: " + result.dest)
    # Send the translated text and info about origin and destination languages
    msg = 'Translated from `' + googletrans.LANGUAGES.get(result.src) + '` ' + emoji_locale.code_to_country(result.src) + ' to `' + googletrans.LANGUAGES.get(result.dest) + '` ' + emoji_locale.code_to_country(result.dest) + '.'
    await ctx.send(msg + '\n```' + result.text[:1950] + '```')

# https://stackoverflow.com/questions/56060614/how-to-make-a-discord-bot-play-youtube-audio
youtube_dl.utils.bug_reports_message = lambda: ''

with open("cookies.txt", "w") as text_file:
    print(os.getenv('COOKIE_DATA'), file=text_file)
    
ytdl_format_options = {
    'cookies': 'cookies.txt',
    'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

import ctypes
import ctypes.util
discord.opus.load_opus(ctypes.util.find_library('opus'))    
vc = None
song_queue = []

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_TOKEN)
def youtube_search(title):
    search_response = youtube.search().list(q=title, part='id,snippet', maxResults=10).execute()
    videos = []
    
    # Parse response
    for search_result in search_response.get('items', []):
        # Only take videos (not channels or playlists)
        if search_result['id']['kind'] == 'youtube#video':
            # Add pairs of ('title - channel' : 'video_id') to list
            videos.append(('`' + search_result['snippet']['title'] + '` - `[' + search_result['snippet']['channelTitle'] + ']`', search_result['id']['videoId']))
        
        # Stop at 5
        if len(videos) == 5:
            return videos
    return videos

BOT_ID = str(os.getenv('BOT_ID'))

# This works properly only on one server at a time
# That's fine since this bot is a 'private' one, only made for one server
@bot.command(name='play', help="Join VC and play music.")
@commands.guild_only()
async def play(ctx, *args):
    # No arguments -> exit
    if not args:
        await ctx.send("Play what? " + basic_emoji.get('Pepega') + '\n' + basic_emoji.get('forsenSmug'))
        await ctx.message.add_reaction(basic_emoji.get('Si'))
        return
    
    # Get voice channel
    channel = None
    try:
        channel = ctx.author.voice.channel
    # User not connected to voice channel -> exit
    except:
        msg = await ctx.send("You're not connected to a voice channel.")
        await msg.add_reaction(basic_emoji.get('Si'))
        return
    
    # Extract youtube video url
    arg = ' '.join(str(i) for i in args)
    url = ''
    
    # URL contained in argument
    if 'youtube.com/watch?v=' in arg or 'youtu.be/' in arg:
        # Assume it's the first 'word' of combined arguments
        url = arg.partition(' ')[0]
    # Else search youtube for video title
    else:
        videos = []
        try:
            videos = youtube_search(arg)
        except:
            msg = await ctx.send(basic_emoji.get('hackerCD') + 'HTTP error. ' + basic_emoji.get('Sadge'))
            await msg.add_reaction(basic_emoji.get('Si'))
            return
        # 0 videos -> exit
        if len(videos) == 0:
            msg = await ctx.send('0 videos found. ' + basic_emoji.get('Sadge'))
            await msg.add_reaction(basic_emoji.get('Si'))
            return
        # 1 video -> we have a winner
        elif len(videos) == 1:
            url = 'https://www.youtube.com/watch?v=' + videos[0][1]
        # Else let user to choose which one they meant
        else:
            poll = ''
            i = 0
            # Only giving 5 choices max
            number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
            valid_numbers = []
            # Iterate over all (5 at most) found videos, pair = ('title - channel' : 'video_id')
            for pair in videos:
                # Add title to message
                poll += number_emojis[i] + '. ' + pair[0] + '\n'
                # Add valid option
                valid_numbers.append(number_emojis[i])
                i += 1
            # Display message with available videos
            msg = await ctx.send(poll)            
            
            # Add options
            for number in valid_numbers:
                await msg.add_reaction(number)
            await msg.add_reaction('❌')
                
            # Checks if added reaction is the one we're waiting for
            def check(reaction, user):
                return user == ctx.message.author and (str(reaction.emoji) in valid_numbers or str(reaction.emoji) == '❌')
                       
            reaction = None
            try:
                # Watch for reaction
                reaction, user = await bot.wait_for('reaction_add', timeout=120, check=check)               
            except asyncio.TimeoutError:
                await ctx.send('No option chosen (timed out) ' + basic_emoji.get('Si'))
                return
            # Create chosen URL
            else:
                if str(reaction.emoji) == '❌':
                    await msg.delete()
                    return
                url = 'https://www.youtube.com/watch?v=' + videos[valid_numbers.index(str(reaction.emoji))][1]
            # Delete poll
            await msg.delete()
        
    global vc
    if vc is None:
        vc = await channel.connect()
    else:
        await vc.move_to(channel)
        
    global song_queue
    song_queue.append(url)
    if vc.is_playing():
        await ctx.send('Song added to queue.')
        return
    
    while song_queue:
        song = song_queue.pop(0)
        player = None
        status = None
        # Attempt to download video
        try:
            status = await ctx.send('Downloading... ' + basic_emoji.get('docSpin'))
            player = await YTDLSource.from_url(song, loop=bot.loop)
        except:
            await status.delete()
            await ctx.send('Failed downloading `' + song + '` ' + basic_emoji.get('Si'))
            continue

        await status.delete()
        vc.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        title = await ctx.send(random.choice(dance_emoji) + ' 🎶 Now playing 🎶: `' + player.title + '` ' + random.choice(dance_emoji))
        await title.add_reaction(random.choice(dance_react))

        while vc.is_playing():
            await asyncio.sleep(1)
    await vc.disconnect()
    vc = None
    
@bot.command(name='queue', help="Display songs in queue.")
@commands.guild_only()
async def queue(ctx):
    global song_queue
    if not song_queue:
        await ctx.send('Queue is empty.')
        return
    msg = ''
    for song in song_queue:
        msg += song + '\n'
    await ctx.send('🎶 Queue 🎶: ' + msg[:1980])
        
@bot.command(name='clear', help="Clear song queue.")
@commands.guild_only()
async def clear(ctx):
    global song_queue
    if not song_queue:
        await ctx.send('Queue already empty ' + basic_emoji.get('forsenScoots'))
        return
    song_queue = []
    await ctx.send('Queue emptied.')
    
@bot.command(name='skip', help="Skip current song.")
@commands.guild_only()
async def skip(ctx):
    global vc
    try:
        vc.stop()
    except:
        msg = await ctx.send("Nothing is playing.")
        await msg.add_reaction(basic_emoji.get('Si'))
        
@bot.command(name='stop', aliases=['leave'], help="Stop playing and leave voice.")
@commands.guild_only()
async def stop(ctx):
    global vc
    global song_queue
    song_queue = []
    try:
        vc.stop()
    except:
        msg = await ctx.send("Nothing is playing.")
        await msg.add_reaction(basic_emoji.get('Si'))
    
bot.run(DISCORD_TOKEN)
