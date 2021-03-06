import json
import os
import sys
from datetime import datetime
from random import randint

import discord
# from pyaxie_utils import get_battle_image
import requests
from discord.ext import commands
from discord.utils import get

from utils.database_handling import Database

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

prefix = config['bot_prefix']


def has_roles(context):
    roles = [role.name for role in context.message.author.roles]
    if "Admin" in roles:
        return True
    return False


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.db = Database()
        self.bot = bot
        self.url = "https://graphql-gateway.axieinfinity.com/graphql"
        self.url_api = "https://game-api.skymavis.com/game-api/"
        self.graphql_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'authorization': ""
        }
        self.rapid_api_header = {
            'x-rapidapi-host': 'axie-infinity.p.rapidapi.com',
            'x-rapidapi-key': '4d6d236824mshdc78ed0afdf5344p1f5129jsn24a1446067e9'
        }

    @staticmethod
    def axie_embed(axie):
        embed = discord.Embed(color=randint(0, 0xffff),
                              description=f":{(axie['class']).lower().strip()}: {axie['id']} - {axie['name']}")
        embed.add_field(name='Breed', value=f"**Breed Count:** {axie['breedCount']}/7\n")
        # f"**Purity:** {axie['purity']}/6"
        # f"**Quality:** {axie['quality']}%")
        hyperlink = f"[{axie['ownerProfile']['name']}](https://marketplace.axieinfinity.com/profile/{axie['owner'].replace('0x', 'ronin:')}/)"
        embed.add_field(name='Owner', value=hyperlink)
        embed.add_field(name='Birthdate',
                        value=str(datetime.fromtimestamp(int(axie['birthDate'])).strftime('%Y-%m-%d %H:%M:%S')))
        embed.add_field(name=':green_heart: Health', value=axie['stats']['hp'])
        embed.add_field(name='??? Speed', value=axie['stats']['speed'])
        embed.add_field(name=':star2: Skill', value=axie['stats']['skill'])
        embed.add_field(name=':heart_on_fire: Morale', value=axie['stats']['morale'])
        embed.set_image(url=axie['image'])
        embed.set_footer(text="Data shown is from cache and may be inaccurate.")
        return embed

    @commands.command(name="axie",
                      description=f"Shows the information of the specified axie (Purity, Quality %, Breed Count, "
                                  f"Genes & etc.). Syntax: '<prefix>axie <axie id>'")
    async def axie(self, context, id):
        body = {"operationName": "GetAxieDetail",
                "variables": {"axieId": id},
                "query": "query GetAxieDetail($axieId: ID!) {\n  axie(axieId: $axieId) {\n    ...AxieDetail\n    __typename\n  }\n}\n\nfragment AxieDetail on Axie {\n  id\n  image\n  class\n  chain\n  name\n  genes\n  owner\n  birthDate\n  bodyShape\n  class\n  sireId\n  sireClass\n  matronId\n  matronClass\n  stage\n  title\n  breedCount\n  level\n  figure {\n    atlas\n    model\n    image\n    __typename\n  }\n  parts {\n    ...AxiePart\n    __typename\n  }\n  stats {\n    ...AxieStats\n    __typename\n  }\n  auction {\n    ...AxieAuction\n    __typename\n  }\n  ownerProfile {\n    name\n    __typename\n  }\n  battleInfo {\n    ...AxieBattleInfo\n    __typename\n  }\n  children {\n    id\n    name\n    class\n    image\n    title\n    stage\n    __typename\n  }\n  __typename\n}\n\nfragment AxieBattleInfo on AxieBattleInfo {\n  banned\n  banUntil\n  level\n  __typename\n}\n\nfragment AxiePart on AxiePart {\n  id\n  name\n  class\n  type\n  specialGenes\n  stage\n  abilities {\n    ...AxieCardAbility\n    __typename\n  }\n  __typename\n}\n\nfragment AxieCardAbility on AxieCardAbility {\n  id\n  name\n  attack\n  defense\n  energy\n  description\n  backgroundUrl\n  effectIconUrl\n  __typename\n}\n\nfragment AxieStats on AxieStats {\n  hp\n  speed\n  skill\n  morale\n  __typename\n}\n\nfragment AxieAuction on Auction {\n  startingPrice\n  endingPrice\n  startingTimestamp\n  endingTimestamp\n  duration\n  timeLeft\n  currentPrice\n  currentPriceUSD\n  suggestedPrice\n  seller\n  listingIndex\n  state\n  __typename\n}\n"}

        response = ((requests.post(self.url, json=body, headers=self.graphql_header)).json())['data']['axie']
        embed = self.axie_embed(response)
        await context.reply(content=context.message.author.mention, embed=embed)

    @commands.command(name="axies",
                      description=f"Shows the list of Axies of the specified address (25 Max Axies). Syntax: '<prefix>axies <ronin:address> [sort type] [auction type]'")
    async def axies(self, context, ronin_address, sort_type="", auction_type=""):
        ronin_address = ronin_address.replace("ronin:", "0x")
        if sort_type and auction_type == "":
            body = {"operationName": "GetAxieBriefList",
                    "variables": {"from": 0, "size": 24, "sort": {sort_type},
                                  "owner": ronin_address,
                                  "criteria": {"region": None, "parts": None, "bodyShapes": None, "classes": None,
                                               "stages": None, "numMystic": None, "pureness": None, "title": None,
                                               "breedable": None, "breedCount": None, "hp": [], "skill": [],
                                               "speed": [],
                                               "morale": []}},
                    "query": "query GetAxieBriefList($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {\n  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {\n    total\n    results {\n      ...AxieBrief\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieBrief on Axie {\n  id\n  name\n  stage\n  class\n  breedCount\n  image\n  title\n  battleInfo {\n    banned\n    __typename\n  }\n  auction {\n    currentPrice\n    currentPriceUSD\n    __typename\n  }\n  parts {\n    id\n    name\n    class\n    type\n    specialGenes\n    __typename\n  }\n  __typename\n}\n"}

        elif auction_type and sort_type == "":
            body = {"operationName": "GetAxieBriefList",
                    "variables": {"from": 0, "size": 24, "auctionType": {auction_type},
                                  "owner": ronin_address,
                                  "criteria": {"region": None, "parts": None, "bodyShapes": None, "classes": None,
                                               "stages": None, "numMystic": None, "pureness": None, "title": None,
                                               "breedable": None, "breedCount": None, "hp": [], "skill": [],
                                               "speed": [],
                                               "morale": []}},
                    "query": "query GetAxieBriefList($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {\n  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {\n    total\n    results {\n      ...AxieBrief\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieBrief on Axie {\n  id\n  name\n  stage\n  class\n  breedCount\n  image\n  title\n  battleInfo {\n    banned\n    __typename\n  }\n  auction {\n    currentPrice\n    currentPriceUSD\n    __typename\n  }\n  parts {\n    id\n    name\n    class\n    type\n    specialGenes\n    __typename\n  }\n  __typename\n}\n"}

        elif sort_type and auction_type:
            body = {"operationName": "GetAxieBriefList",
                    "variables": {"from": 0, "size": 24, "sort": {sort_type}, "auctionType": {auction_type},
                                  "owner": ronin_address,
                                  "criteria": {"region": None, "parts": None, "bodyShapes": None, "classes": None,
                                               "stages": None, "numMystic": None, "pureness": None, "title": None,
                                               "breedable": None, "breedCount": None, "hp": [], "skill": [],
                                               "speed": [],
                                               "morale": []}},
                    "query": "query GetAxieBriefList($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {\n  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {\n    total\n    results {\n      ...AxieBrief\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieBrief on Axie {\n  id\n  name\n  stage\n  class\n  breedCount\n  image\n  title\n  battleInfo {\n    banned\n    __typename\n  }\n  auction {\n    currentPrice\n    currentPriceUSD\n    __typename\n  }\n  parts {\n    id\n    name\n    class\n    type\n    specialGenes\n    __typename\n  }\n  __typename\n}\n"}

        else:
            body = {"operationName": "GetAxieBriefList",
                    "variables": {"from": 0, "size": 24, "owner": ronin_address,
                                  "criteria": {"region": None, "parts": None, "bodyShapes": None, "classes": None,
                                               "stages": None, "numMystic": None, "pureness": None, "title": None,
                                               "breedable": None, "breedCount": None, "hp": [], "skill": [],
                                               "speed": [],
                                               "morale": []}},
                    "query": "query GetAxieBriefList($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {\n  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {\n    total\n    results {\n      ...AxieBrief\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieBrief on Axie {\n  id\n  name\n  stage\n  class\n  breedCount\n  image\n  title\n  battleInfo {\n    banned\n    __typename\n  }\n  auction {\n    currentPrice\n    currentPriceUSD\n    __typename\n  }\n  parts {\n    id\n    name\n    class\n    type\n    specialGenes\n    __typename\n  }\n  __typename\n}\n"}

        r = requests.post(self.url, headers=self.graphql_header, json=body)
        r = r.json()
        axies = r["data"]['axies']['results']
        axies = axies[0:2]
        await context.reply(
            content=f"({self.get_name(ronin_address)})[(https://marketplace.axieinfinity.com/profile/{ronin_address}/axie)]'s axies: ")
        for i in axies:
            await context.reply(embed=self.axie_embed(i))

    @staticmethod
    def get_name(ronin_address):
        response = requests.get(f"https://game-api.axie.technology/api/v1/{ronin_address}/")
        response = response.json()
        return response['name']

    def get_result(self, battle, ronin_address):
        if battle['first_client_id'] == ronin_address:
            if battle['winner'] == 0:
                return ["Won", battle['second_client_id']]
            else:
                return ["Defeated", battle['second_client_id']]
        elif battle['second_client_id'] == ronin_address:
            if battle['winner'] == 1:
                return ["Won", battle['first_client_id']]
            else:
                return ["Defeated", battle['first_client_id']]

    def get_team(self, team_list):
        rtn = ""
        for i in team_list:
            if i['fighter_class'] == "Plant":
                rtn += f"\n:plant: [{i['fighter_id']}](https://marketplace.axieinfinity.com/axie/{i['fighter_id']})"
            elif i['fighter_class'] == "Reptile":
                rtn += f"\n:reptile: [{i['fighter_id']}](https://marketplace.axieinfinity.com/axie/{i['fighter_id']})"
            elif i['fighter_class'] == "Dusk":
                rtn += f"\n:dusk: [{i['fighter_id']}](https://marketplace.axieinfinity.com/axie/{i['fighter_id']})"
            elif i['fighter_class'] == "Aquatic":
                rtn += f"\n:aquatic: [{i['fighter_id']}](https://marketplace.axieinfinity.com/axie/{i['fighter_id']})"
            elif i['fighter_class'] == "Bird":
                rtn += f"\n:bird: [{i['fighter_id']}](https://marketplace.axieinfinity.com/axie/{i['fighter_id']})"
            elif i['fighter_class'] == "Dawn":
                rtn += f"\n:dawn: [{i['fighter_id']}](https://marketplace.axieinfinity.com/axie/{i['fighter_id']})"
            elif i['fighter_class'] == "Beast":
                rtn += f"\n:beast: [{i['fighter_id']}](https://marketplace.axieinfinity.com/axie/{i['fighter_id']})"
            elif i['fighter_class'] == "Bug":
                rtn += f"\n:bug: [{i['fighter_id']}](https://marketplace.axieinfinity.com/axie/{i['fighter_id']})"
            elif i['fighter_class'] == "Mech":
                rtn += f"\n:mech: [{i['fighter_id']}](https://marketplace.axieinfinity.com/axie/{i['fighter_id']})"
        return rtn

    # @commands.command(name="battles",
    #                   description=f" Shows recent arena battles of the specified address (25 Recent Battles). Syntax: '<prefix>battles <ronin:address>'")
    # async def battles(self, context, ronin_address):
    #     ronin_address = ronin_address.replace('ronin:', '0x')
    #     r = requests.get(f"https://game-api.skymavis.com/game-api/clients/{ronin_address}/battles")
    #     r = r.json()
    #     battles = list()
    #     if r[0]['success']:
    #         r = r[0]['items'][0:5]
    #         flag = 0
    #         for battle in r:
    #             if flag <= 9:
    #                 flag += 1
    #                 l = list()
    #                 for i in battle['fighters']:
    #                     l.append(i['fighter_id'])
    #
    #                 path = get_battle_image(l)
    #                 file = discord.File(path)
    #                 result = self.get_result(battle, ronin_address)
    #                 embed = discord.Embed(color=randint(0, 0xffff), description=f"**{self.get_name(ronin_address)}'s recent battles**")
    #                 embed.add_field(name='Result', value=result[0])
    #                 embed.add_field(name=chr(137), value=chr(137))
    #                 embed.add_field(name='Opponent', value=f"[{await self.get_name(result[1])}]('https://marketplace.axieinfinity.com/profile/{ronin_address}/axie')")
    #                 embed.add_field(name="Team", value=self.get_team(battle['fighters'][0:3]))
    #                 embed.add_field(name=chr(137), value=chr(137))
    #                 embed.add_field(name="Opponent Team", value=self.get_team(battle['fighters'][3:6]))
    #                 embed.set_image(url=f"attachment://{path}")
    #                 embed.timestamp = datetime.now()
    #                 battles.append((embed, file))
    #             else:
    #                 break
    #         if battles:
    #             for i in battles:
    #                 await context.reply(embed=i[0], file=i[1])
    #             return

    @commands.command(name="lb",
                      description=f"Axie Infinity leaderboard for current season (Top 100 Players). Syntax: '<prefix>leaderboard'")
    async def leaderboard(self, context):
        params = {"offset": 0, "limit": 36}
        try:
            r = requests.get(self.url_api + "last-season-leaderboard", params=params)
            json_data = r.json()
            if json_data['success']:
                json_data = json_data['items']
                description = ""
                for i in json_data:
                    description += f"**{(i['client_id']).replace('0x', 'ronin:')}**\n**Name:** {i['name']} | **Rank:** {i['rank']} | **ELO:** {i['elo']}\n\n"
                embed = discord.Embed(color=randint(0, 0xffff), description=description)
                await context.reply(embed=embed)
        except ValueError as e:
            return e

    @commands.command(name="peek",
                      description=f"Shows the image of the specified axie. Syntax: '<prefix>peek <axie id>'")
    async def peek(self, context, id):
        body = {"operationName": "GetAxieDetail",
                "variables": {"axieId": id},
                "query": "query GetAxieDetail($axieId: ID!) {\n  axie(axieId: $axieId) {\n    ...AxieDetail\n    __typename\n  }\n}\n\nfragment AxieDetail on Axie {\n  id\n  image\n  class\n  chain\n  name\n  genes\n  owner\n  birthDate\n  bodyShape\n  class\n  sireId\n  sireClass\n  matronId\n  matronClass\n  stage\n  title\n  breedCount\n  level\n  figure {\n    atlas\n    model\n    image\n    __typename\n  }\n  parts {\n    ...AxiePart\n    __typename\n  }\n  stats {\n    ...AxieStats\n    __typename\n  }\n  auction {\n    ...AxieAuction\n    __typename\n  }\n  ownerProfile {\n    name\n    __typename\n  }\n  battleInfo {\n    ...AxieBattleInfo\n    __typename\n  }\n  children {\n    id\n    name\n    class\n    image\n    title\n    stage\n    __typename\n  }\n  __typename\n}\n\nfragment AxieBattleInfo on AxieBattleInfo {\n  banned\n  banUntil\n  level\n  __typename\n}\n\nfragment AxiePart on AxiePart {\n  id\n  name\n  class\n  type\n  specialGenes\n  stage\n  abilities {\n    ...AxieCardAbility\n    __typename\n  }\n  __typename\n}\n\nfragment AxieCardAbility on AxieCardAbility {\n  id\n  name\n  attack\n  defense\n  energy\n  description\n  backgroundUrl\n  effectIconUrl\n  __typename\n}\n\nfragment AxieStats on AxieStats {\n  hp\n  speed\n  skill\n  morale\n  __typename\n}\n\nfragment AxieAuction on Auction {\n  startingPrice\n  endingPrice\n  startingTimestamp\n  endingTimestamp\n  duration\n  timeLeft\n  currentPrice\n  currentPriceUSD\n  suggestedPrice\n  seller\n  listingIndex\n  state\n  __typename\n}\n"}

        response = ((requests.post(self.url, json=body, headers=self.graphql_header)).json())['data']['axie']
        embed = discord.Embed(color=randint(0, 0xffff))
        embed.set_image(url=response['image'])
        await context.reply(content=context.message.author.mention, embed=embed)

    @commands.command(name="removeronin",
                      description=f"Remove your ronin:address from your account. For removing: '<prefix>removeronin'")
    async def removeronin(self, context):
        r = self.db.remove_ronin_db(context.author.id)
        await context.reply(embed=discord.Embed(color=randint(0, 0xffff), description=r))
        return

    @commands.command(name="setronin",
                      description=f"Add ronin:address to your account. For adding: '<prefix>setronin <ronin:address>'")
    async def setronin(self, context, ronin_address):
        r = self.db.set_ronin_db(ronin_address, context.author.id)
        await context.reply(embed=discord.Embed(color=randint(0, 0xffff), description=r))
        return

    def get_avatar(self, ronin_address):
        r = self.db.get_scholar_by_ronin(ronin_address)
        if r:
            return r[0]
        return

    @commands.command(name="stats",
                      description=f"Get the Player Stats of specified ronin:address (Current Balance, Unclaimed SLP, Total SLP, Claim Dates & etc.). Syntax: '<prefix>stats <ronin:address>'")
    async def stats(self, context, ronin_address=None):
        try:
            if '@' in ronin_address:
                discord_id = int((ronin_address.replace('<@!', '')[:-1]))
                r = self.db.get_ronin_by_id(discord_id)
                if r:
                    ronin_address = r
                else:
                    return await context.reply(content=context.author.mention, embed=discord.Embed(color=0xfffff,
                                                                                                   description="*Mentioned user wasn't found in the database*"))
            elif 'ronin:' in ronin_address or '0x' in ronin_address:
                ronin_address = ronin_address.replace('ronin:', '0x')
        except:
            r = self.db.get_ronin_by_id(context.author.id)
            if r:
                ronin_address = r
            else:
                return await context.reply(content=context.author.mention, embed=discord.Embed(color=0xfffff,
                                                                                               description="*Your account wasn't found in the database*"))
        try:
            id_avatar = self.get_avatar(ronin_address)
            r = ((requests.get(
                f"https://game-api.axie.technology/api/v1/{(ronin_address)}")).json())
            scholar_percentage = self.db.get_scholar_percentage(ronin=ronin_address)
            if r['success']:
                embed = discord.Embed(color=randint(0, 0xffff),
                                      description=f"**Axie Infinity Profile: [{r['name']}](https://marketplace.axieinfinity.com/profile/{ronin_address}/axie)** \n\n**{ronin_address.replace('0x', 'ronin:')}**\n")
                if id_avatar:
                    member = get(self.bot.get_all_members(), id=id_avatar)
                    if member:
                        embed.set_thumbnail(url=member.avatar_url)
                embed.add_field(name='????Rank', value=r['rank'])
                embed.add_field(name='????MMR', value=r['mmr'])
                embed.add_field(name='???Matches', value=r['total_matches'])
                embed.add_field(name='????Win Rate', value=r['win_rate'])
                embed.add_field(name='???????Wins', value=r['win_total'])
                embed.add_field(name='????Losses', value=r['lose_total'])
                embed.add_field(name='???????Draws', value=r['draw_total'])
                embed.add_field(name='<:SLP:896085115803955242> Daily SLP',
                                value=str(self.get_daily_slp(ronin_address)[0]))
                embed.add_field(name='<:SLP:896085115803955242> SLP Current Balance', value=r['in_game_slp'])
                embed.add_field(name='<:SLP:896085115803955242> Total SLP', value=r['total_slp'])
                if scholar_percentage:
                    percent = self.get_unclaimed_slp(ronin_address) * scholar_percentage
                    embed.add_field(name='<:SLP:896085115803955242> Scholar Share', value=str(percent))
                else:
                    embed.add_field(name='<:SLP:896085115803955242> Scholar Share', value=str(scholar_percentage))

                embed.add_field(name='<:SLP:896085115803955242> Average SLP',
                                value=str(self.get_daily_slp(ronin_address)[1]))
                embed.add_field(name='???????Next SLP Claim',
                                value=datetime.fromtimestamp(int(f"{r['next_claim']}")).strftime(
                                    '%Y-%m-%d %H:%M:%S'))
                if scholar_percentage:
                    php, usd = self.convert_slp(self.get_unclaimed_slp(ronin_address) * scholar_percentage)
                    embed.add_field(name='???PHP Conversion', value=str(round(php, 2)))
                    embed.add_field(name='$USD Conversion', value=str(round(usd, 2)))
                else:
                    embed.add_field(name='???PHP Conversion', value=str(scholar_percentage))
                    embed.add_field(name='$USD Conversion', value=str(scholar_percentage))
                return await context.reply(embed=embed)
        except Exception as e:
            print(e)

    @staticmethod
    def convert_slp(slp):
        php = \
        requests.get('https://api.coingecko.com/api/v3/simple/price?ids=smooth-love-potion&vs_currencies=php').json()[
            'smooth-love-potion']['php']
        usd = \
        requests.get('https://api.coingecko.com/api/v3/simple/price?ids=smooth-love-potion&vs_currencies=usd').json()[
            'smooth-love-potion']['usd']
        return slp * php, slp * usd

    @commands.command(name="share",
                      description=f"Set your scholar share. Syntax: '<prefix>share <percentage>'")
    async def set_share(self, context, percentage):
        ronin_address = None
        try:
            percentage = int(percentage)
        except:
            percentage = int(percentage.replace('%', ''))

        if percentage > 1:
            percentage = percentage / 100

        if percentage < 0.25 or percentage > 0.6:
            return await context.reply(content=context.author.id, embed=discord.Embed(color=0xffff,
                                                                                      description="*Share can only be between 40-60%. Please try again.*"))

        r = self.db.set_scholar_percentage(context.author.id, percentage)
        await context.reply(embed=discord.Embed(color=randint(0, 0xffff), description=r))

    @commands.command(name="removeshare",
                      description=f"Remove your scholar share. Syntax: '<prefix>removeshare'")
    async def remove_share(self, context):
        r = self.db.delete_percentage(context.author.id)
        await context.reply(embed=discord.Embed(color=randint(0, 0xffff), description=r))

    @staticmethod
    def get_total_slp(ronin_address):
        r = requests.get(f"https://game-api.axie.technology/api/v1/{ronin_address.replace('ronin:', '0x')}/")
        r = r.json()
        return r['total_slp']

    def get_daily_slp(self, ronin_address):
        ronin_address = ronin_address.replace('ronin:', '0x')
        url = f"https://axie-infinity.p.rapidapi.com/get-update/{ronin_address}"
        r = requests.get(url=url, headers=self.rapid_api_header, params={'id': ronin_address}).json()
        return r['slp']['todaySoFar'], r['slp']['average']

    def get_unclaimed_slp(self, ronin_address):
        """
        :param ronin_address: Ronin address to check
        :return: The amount of unclaimed SLP
        """
        try:
            response = requests.get(self.url_api + f"clients/{ronin_address}/items/1", headers=self.graphql_header,
                                    data="")
            result = response.json()
        except ValueError as e:
            return e
        if result is None:
            return 0

        balance = -1
        if 'blockchain_related' in result:
            balance = result['blockchain_related']['balance']
        else:
            return balance
        if balance is None:
            balance = 0

        res = result["total"]
        if res is None:
            res = 0
        return int(res - balance)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, (commands.CommandNotFound, discord.HTTPException)):
            return

        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=discord.Embed(
                title="Error",
                description="You don't have the permission to use this command."))
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(
                title="Error",
                description=f"You forgot to provide an argument, please do it like: `{ctx.command.name} {ctx.command.usage}`"))


def setup(bot):
    bot.add_cog(General(bot))
