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

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
GOOGLE_CLOUD_CREDENTIALS = service_account.Credentials.from_service_account_info(json.loads(os.getenv('GOOGLE_CLIENT_SECRETS')))

bot = commands.Bot(command_prefix='p.')

si_emoji = '<:Si:523966164704034837>'
smug_emoji = '<:forsenSmug:736973361283858442>'
sad_emoji = '<:Sadge:696437945392955453>'
pepega_emoji = '<:Pepega:739020602194657330>'
scoots_emoji = [
    '<:forsenScoots:736973346142552195>',
    '<:OMGScoots:736973384570634321>'
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
        await ctx.message.add_reaction(si_emoji)
        await ctx.send(pepega_emoji + '📣' + ' COMMAND NOT FOUND')
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
    status = await channel.send('Sending HTTP request...')
    response = None
    try:
        response = requests.get(url, headers)
        response.raise_for_status()
    except:
        fail = await channel.send('Bad response from ' + url + '.')
        await status.delete()
        await fail.add_reaction(si_emoji)
        return
    await status.edit(content='Parsing ' + str(round((len(response.content)/1024.0),2)) + 'kB...')
    soup = BeautifulSoup(response.content, 'html.parser')
    await status.edit(content='Looking for Garfield comic...')
    picture = soup.find_all('picture', attrs={'class': 'item-comic-image'})
    if not picture or not picture[0]:
        fail = await channel.send('Garfield comic not found on ' + url + '.')
        await status.delete()
        await fail.add_reaction(si_emoji)
        return
    await status.edit(content='Garfield comic found.')
    link = picture[0].img['src']
    await status.delete()
    await channel.send(link)

@bot.command(name='roll', help='Generate a random number between 1 and 100 by default.')
async def roll(ctx, input: str = '100'):
    result = "No, I don't think so. " + smug_emoji
    if input.isnumeric():
        result = str(random.randint(1, int(input)))
    else:
        await ctx.message.add_reaction(si_emoji)
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
    await ctx.message.add_reaction(si_emoji)
    await ctx.send(response)

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

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
    status = await ctx.send('Looking up an interesting fact...')
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
        fact = await ctx.send("Couldn't access wikipedia entry. " + sad_emoji + '\nThis comic came out in ' + custom_strftime('%B {S}, %Y', rd) + '.')
    elif not facts:
        await status.delete()
        fact = await ctx.send("Didn't find any interesting fact on wikipedia.com/wiki/" + rd.strftime('%B') + '_' + str(rd.day) + ". Probably retarded formatting on this page for the 'events' section." + sad_emoji )
    else:
        await status.delete()
        fact = await ctx.send('This comic came out in ' + custom_strftime('%B {S}, %Y', rd) + '. On this day also in the year ' + random.choice(facts))
        await fact.add_reaction(random.choice(scoots_emoji))

@bot.command(name='garf', help="Get specific Garfield comic, format: 'Year Month Day'.")
async def garf(ctx, arg1: str = '', arg2: str = '', arg3: str = ''):
    result = "No, I don't think so. " + smug_emoji
    if not arg1 or not arg2 or not arg3:
        result = "Date looks like 'Year Month Day', ie. '2001 9 11' :)."
        await ctx.message.add_reaction(si_emoji)
    elif not arg1.isnumeric() or not arg2.isnumeric() or not arg3.isnumeric():
        result = "That's not even a numeric date."
        await ctx.message.add_reaction(si_emoji)
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
            await ctx.message.add_reaction(si_emoji)
        elif newDate > now:
            result = 'You will have to wait for that day to come.'
            await ctx.message.add_reaction(si_emoji)
        elif newDate >= datetime.date(1978, 6, 19):
            result = ''
            await garf_comic(ctx.channel, datetime.date(a1, a2, a3))
        else:
            result = "Unfortunately, Garfield didn't exist before 19th June 1978."
            await ctx.message.add_reaction(si_emoji)
    if result:
        await ctx.send(result)

@bot.command(name='weather', help="Get location's weather.")
async def weather(ctx, *args):
    city = 'Prague'
    if len(args) != 0:
        city = '' ''.join(map(str, args))
    url = ('http://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=en&appid=' + WEATHER_TOKEN)
    res = requests.get(url).json()
    if str(res['cod']) == '200':
        description = 'Weather in ' + res['name'] + ', ' + res['sys']['country']
        embed = discord.Embed(title='Weather', description=description)
        image = 'http://openweathermap.org/img/w/' + res['weather'][0]['icon'] + '.png'
        embed.set_thumbnail(url=image)
        weather = res['weather'][0]['main'] + ' ( ' + res['weather'][0]['description'] + ' ) '
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
        msg = await ctx.send('City not found')
        await msg.add_reaction(sad_emoji)
    elif str(res['cod']) == '401':
        msg = await ctx.send('API key broke, have a nice day.')
        await msg.add_reaction(si_emoji)
    else:
        await ctx.send('City not found! ' + sad_emoji + ' (' + res['message'] + ')')

@bot.command(name='fact', help="Get random fact about a day.")
async def fact(ctx, arg1: str = '', arg2: str = ''):
    date = None
    msg = ''
    if not arg1 or not arg2:
        date = datetime.datetime.today()
        msg = 'On this day in the year '
    elif not arg1.isnumeric() or not arg2.isnumeric():
        await ctx.send("That's not even a numeric date. Try 'Month Day'.")
        await ctx.message.add_reaction(si_emoji)
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
            await ctx.message.add_reaction(si_emoji)
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
        fact = await ctx.send("Couldn't access wikipedia entry " + sad_emoji)
    elif not facts:
        await status.delete()
        fact = await ctx.send("Didn't find any interesting fact on wikipedia.com/wiki/" + date.strftime('%B') + '_' + str(date.day) + ". Probably retarded formatting on this page for the 'events' section." + sad_emoji )
    else:
        await status.delete()
        fact = await ctx.send(msg + random.choice(facts))
        await fact.add_reaction(random.choice(scoots_emoji))

google_vision = vision.ImageAnnotatorClient(credentials=GOOGLE_CLOUD_CREDENTIALS)

def detect_text(url):
    response = requests.get(url)
    image = None
    try:
        image_bytes = io.BytesIO(response.content)
        image = vision.types.Image(content=image_bytes.read())
    except:
        return "Couldn't download image."
    cloud_response = google_vision.text_detection(image=image)
    texts = cloud_response.text_annotations
    if not texts:
        return 'No text detected.'
    else:
        return texts[0].description

@bot.command(name='read', help='Read image.')
async def read(ctx, arg1: str = ''):
    if not arg1 and not ctx.message.attachments:
        await ctx.send('No image provided.')
        await ctx.message.add_reaction(si_emoji)
        return
    url = ''
    if arg1:
        url = arg1
    else:
        url = ctx.message.attachments[0].url
    status = await ctx.send('Processing...')
    text = ''
    try:
        text = '```' + detect_text(url)[:1994] + '```'
    except:
        await status.delete()
        await ctx.send("No, I don't think so. " + smug_emoji)
        await ctx.message.add_reaction(si_emoji)
        return
    await status.delete()
    await ctx.send(text)
    
translator = googletrans.Translator()

@bot.command(name='translate', help="Translate text.")
async def translate(ctx, *, arg):
    result = None
    
    # No text entered -> nothing to translate
    if not arg:
        await ctx.send("No, I don't think so. " + smug_emoji)
        await ctx.message.add_reaction(si_emoji)
        return
    
    # Get first word
    input = arg.split(' ', 1)
    # If it's an ISO639-1 language code, translate to that language
    if input[0] in googletrans.LANGUAGES:
        result = translator.translate(input[1], dest=input[0])
    # Otherwise translate to english by default
    else:
        result = translator.translate(arg, dest='en')
        
    # Send the translated text and info about origin and destination languages
    msg = 'Translated from `' + googletrans.LANGUAGES.get(result.src) + '` ' + emoji_locale.code_to_country(result.src) + ' to `' + googletrans.LANGUAGES.get(result.dest) + '` ' + emoji_locale.code_to_country(result.dest) + '.'
    await ctx.send(msg + '\n```' + result.text[:1900] + '```')

# https://stackoverflow.com/questions/56060614/how-to-make-a-discord-bot-play-youtube-audio
youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
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
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

raise OpusNotLoaded()
discord.opus.OpusNotLoaded
import ctypes
import ctypes.util
print("ctypes - Find opus:")
a = ctypes.util.find_library('opus')
print(a)
print("Discord - Load Opus:")
b = discord.opus.load_opus(a)
print(b)
print("Discord - Is loaded:")
c = discord.opus.is_loaded()
print(c)
    
@bot.command(pass_context=True)
async def play(ctx, *, url):
    player = await YTDLSource.from_url(url, loop=bot.loop)
    channel = ctx.author.voice.channel
    vc = await channel.connect()
    vc.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
    #vc.is_playing()
    #vc.pause()
    #vc.resume()
    #vc.stop()
        
    await ctx.send('Now playing: {}'.format(player.title))
    
bot.run(DISCORD_TOKEN)
