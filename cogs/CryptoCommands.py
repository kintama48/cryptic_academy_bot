import datetime
import json
import math
import os
import sys
from random import randint

import discord
import requests
from discord.ext import commands
from pycoingecko import CoinGeckoAPI

from cogs.general import General

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

token = config["token"]
client = discord.Client()

def has_roles(context):
    roles = [role.name for role in context.message.author.roles]
    if "Admin" in roles:
        return True
    return False

prefix = config['bot_prefix']

class CryptoCommands(commands.Cog, name="crypto"):
    def __init__(self, bot):
        self.bot = bot
        self.url = "https://axieinfinity.com/graphql-server-v2/graphql"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'authorization': ""
        }

    @commands.command(name="assets",
                      description=f"Get the Assets/Token Holdings of specified ronin:address (AXS, SLP, WETH, AXIE, LAND, ITEM). Syntax: '<prefix>assets <ronin:address>'")
    async def assets(self, context, ronin_address):
        assets = self.get_account_balances(ronin_address=ronin_address.replace('ronin:', '0x'))
        name = General.get_name(ronin_address=ronin_address.replace('ronin:', '0x'))
        embed = discord.Embed(color=randint(0, 0xfff), description=f"**{name}'s Holdings**\n\n*{ronin_address}*")
        embed.add_field(name='<:Ethereum:869408681362620436> WETH', value=assets['WETH'])
        embed.add_field(name='<:AXS:896085438001979422> AXS', value=assets['AXS'])
        embed.add_field(name='<:SLP:896085115803955242> SLP', value=assets['SLP'])
        embed.add_field(name=':AxieInfinity: Total Axies', value=assets['axies'])
        embed.timestamp = datetime.datetime.now()
        await context.reply(content=context.message.author.mention, embed=embed)

    @commands.command(name="slp",
                      description=f"Shows the current price of SLP (Price, 24H Change %, 24H High, 24H Low). Syntax: '<prefix>slp <currency> <amount>'")
    async def slp(self, context):
        coin = CoinGeckoAPI()
        coin_data = coin.get_coin_by_id(id='smooth-love-potion')['market_data']

        embed = discord.Embed(color=randint(0, 0xffff), description="**<:SLP:896085115803955242> SLP's price in USD and PHP**")
        embed.add_field(name='$USD', value=str(round(coin_data['current_price']['usd'], 2)))
        embed.add_field(name='₱PHP', value=str(round(coin_data['current_price']['php'], 2)))
        embed.add_field(name=':chart_with_upwards_trend: 24h Change Percentage', value=str(round(coin_data["price_change_percentage_24h"], 2)))
        embed.add_field(name=':chart_with_upwards_trend: 24h High', value=f"**$ USD:** {coin_data['high_24h']['usd']}\n"
                                               f"**₱ PHP:** {coin_data['high_24h']['php']}")
        embed.add_field(name=':chart_with_downwards_trend: 24h Low', value=f"**$ USD:** {coin_data['low_24h']['usd']}\n"
                                               f"**₱ PHP:** {coin_data['low_24h']['php']}")

        embed.timestamp = datetime.datetime.now()
        await context.reply(content=context.message.author.mention, embed=embed)
        return

    @commands.command(name="axs",
                      description=f"Shows the current price of AXS. (Price, 24H Change %, 24H High, 24H Low). Syntax: '<prefix>axs'")
    async def axs(self, context):
        coin = CoinGeckoAPI()
        coin_data = coin.get_coin_by_id(id='axie-infinity')['market_data']

        embed = discord.Embed(color=randint(0, 0xffff), description="**<:AXS:896085438001979422> AXS**")
        embed.add_field(name='$USD', value=str(round(coin_data['current_price']['usd'], 2)))
        embed.add_field(name='₱PHP', value=str(round(coin_data['current_price']['php'], 2)))
        embed.add_field(name=':chart_with_upwards_trend: 24h Change Percentage', value=str(round(coin_data["price_change_percentage_24h"], 2)))
        embed.add_field(name=':chart_with_upwards_trend: 24h High', value=f"**$ USD:** {coin_data['high_24h']['usd']}\n"
                                               f"**₱ PHP:** {coin_data['high_24h']['php']}")
        embed.add_field(name=':chart_with_downwards_trend: 24h Low', value=f"**$ USD:** {coin_data['low_24h']['usd']}\n"
                                               f"**₱ PHP:** {coin_data['low_24h']['php']}")

        embed.timestamp = datetime.datetime.now()
        await context.reply(content=context.message.author.mention, embed=embed)
        return

    @commands.command(name="gas",
                      description=f"Shows the gas price or transaction fees of specified currency. Syntax: '<prefix>gas <currency> <detailed>(detailed argument can be True or False)'")
    async def gas(self, context, currency, detailed=False):
        try:
            r = requests.get(f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={config['etherscan_key']}").json()
            slow = r['SafeGasPrice']
            standard = r['SafeGasPrice']
            fast = r['ProposeGasPrice']
            rapid = r['FastGasPrice']
            embed = discord.Embed(color=randint(0, 0xffff))
            if currency.lower().strip() in ['axs', 'php', 'usd']:
                if detailed:
                    calculate_eth_tx = lambda gwei, limit: round(gwei * limit * 0.000000001, 4)
                    r = self.get_gas_from_ethgasstation()
                    fast, standard, slow = r['rapid'], r['fast'], r['standard']
                    eth_price = \
                        requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd').json()[
                            'ethereum'][
                            'usd']
                    simple_tx_fee_eth = calculate_eth_tx(fast, 21000)
                    simple_tx_fee_usd = round(simple_tx_fee_eth * eth_price, 2)
                    token_approve_eth = calculate_eth_tx(fast, 51000)
                    token_approve_usd = round(token_approve_eth * eth_price, 2)
                    token_transfer_eth = calculate_eth_tx(fast, 48000)
                    token_transfer_usd = round(token_transfer_eth * eth_price, 2)
                    range1_uniswap_eth = calculate_eth_tx(fast, 120000)
                    range1_uniswap_usd = round(range1_uniswap_eth * eth_price, 2)
                    range2_uniswap_eth = calculate_eth_tx(fast, 200000)
                    range2_uniswap_usd = round(range2_uniswap_eth * eth_price, 2)
                    fees_eth = f"⛽** [Gas Price](https://axie.live)**\n\n**:rocket: Rapid: {fast}** **:airplane: Fast: {standard}** **:bike: Standard: {slow}**\n"
                    embed.add_field(name="**<:Ethereum:869408681362620436> Simple ETH TX**", value=f"${simple_tx_fee_usd} ({simple_tx_fee_eth} Ξ)")
                    embed.add_field(name="**Token Approval (ERC20):**", value=f'${token_transfer_usd} ({token_transfer_eth} Ξ)')
                    embed.add_field(name='**Token Transfer (ERC20):**', value=f'${token_transfer_usd} ({token_transfer_eth} Ξ)')
                    embed.add_field(name='**Uniswap Trades:**', value=f'${range1_uniswap_usd} - ${range2_uniswap_usd}** ({range1_uniswap_eth} Ξ - {range2_uniswap_eth} Ξ)')
                    embed.timestamp = datetime.datetime.now()
                    embed.description = fees_eth
                    await context.reply(embed=embed)
                    return
                    # if currency.lower() == 'php':
                    #     embed.description = "**[Transaction Fees](https://axie.live)**\n\n" \
                    #                         "MetaMask always shows the maximum possible calculated fee.This shows average actual fee that will be charged." \
                    #                         "\n**Never change the Gas Limit in MetaMask!**\n" \
                    #                         f"**Transactions**              **Rapid|{rapid}|15s**  **Fast|{fast}|1m**\n" \
                    #                         f":ronin:**Ronin Transactions** 0 PHP                  0 PHP\n" \
                    #                         f":ethereum:**Deposit ETH**     \n" \
                    #                         f":ethereum:**Withdraw ETH      \n" \
                    #                         f":axs:**Deposit AXS**     \n" \
                    #                         f":axs:**Withdraw AXS      \n" \
                    #                         f":slp:**Deposit SLP**     \n" \
                    #                         f":slp:**Withdraw SLP      \n" \
                    #                         f":ethereum:**Ethereum: Send ETH**  \n"\
                    #                         f":axs:**Ethereum: Send AXS**\n" \
                    #                         f":slp:**Ethereum: Send SLP**\n"
                    #
                    # elif currency.lower() == 'usd':
                    #     embed.description = "**[Transaction Fees](https://axie.live)**\n\n" \
                    #                         "MetaMask always shows the maximum possible calculated fee.This shows average actual fee that will be charged." \
                    #                         "\n**Never change the Gas Limit in MetaMask!**\n" \
                    #                         f"**Transactions**              **Rapid|{rapid}|15s**  **Fast|{fast}|1m**\n" \
                    #                         f":ronin:**Ronin Transactions** 0 USD                  0 USD" \
                    #                         f":ethereum:**Deposit ETH**     \n" \
                    #                         f":ethereum:**Withdraw ETH      \n" \
                    #                         f":axs:**Deposit AXS**     \n" \
                    #                         f":axs:**Withdraw AXS      \n" \
                    #                         f":slp:**Deposit SLP**     \n" \
                    #                         f":slp:**Withdraw SLP      \n" \
                    #                         f":ethereum:**Ethereum: Send ETH**  \n" \
                    #                         f":axs:**Ethereum: Send AXS**\n" \
                    #                         f":slp:**Ethereum: Send SLP**\n"
                    #
                    # elif currency.lower() == 'axs':
                    #     embed.description = "**[Transaction Fees](https://axie.live)**\n\n" \
                    #                         "MetaMask always shows the maximum possible calculated fee.This shows average actual fee that will be charged." \
                    #                         "\n**Never change the Gas Limit in MetaMask!**\n" \
                    #                         f"**Transactions**              **Rapid|{rapid}|15s**  **Fast|{fast}|1m**\n" \
                    #                         f":ronin:**Ronin Transactions** 0 AXS                  0 AXS" \
                    #                         f":ethereum:**Deposit ETH**     \n" \
                    #                         f":ethereum:**Withdraw ETH      \n" \
                    #                         f":axs:**Deposit AXS**     \n" \
                    #                         f":axs:**Withdraw AXS      \n" \
                    #                         f":slp:**Deposit SLP**     \n" \
                    #                         f":slp:**Withdraw SLP      \n" \
                    #                         f":ethereum:**Ethereum: Send ETH**  \n" \
                    #                         f":axs:**Ethereum: Send AXS**\n" \
                    #                         f":slp:**Ethereum: Send SLP**\n"
                    #
                    # await context.reply(content=context.message.author.mention, embed=embed)
                    # return
                else:
                    embed = discord.Embed(color=randint(0, 0xffff), description="⛽** [Gas Price](https://axie.live)**\n")
                    embed.add_field(name="**:rocket: Rapid**", value=f'**{rapid}**|15 seconds')
                    embed.add_field(name="**:airplane: Fast**", value=f'**{fast}**|1 minute')
                    embed.add_field(name="**:red_car: Standard**", value=f'**{standard}**|3 minutes')
                    embed.add_field(name="**:bike: Slow**", value=f'**{slow}**|>10 minutes')
                    embed.timestamp = datetime.datetime.now()
                    await context.reply(content=context.message.author.mention, embed=embed)
            else:
                embed = discord.Embed(color=0xffff, description="Invalid currency entered.")
                await context.reply(content=context.message.author.menton, embed=embed)
                return
        except:
            pass

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

    @staticmethod
    def get_account_balances(ronin_address):
        """
        Get the different balances for a given account (AXS, SLP, WETH, AXIES)
        :param ronin_address: ronin address of the account
        :return: dict with currencies and amount
        """
        # if not ronin_address:
        #     ronin_address = self.config['personal']['ronin_address']

        url = "https://explorer.roninchain.com/api/tokenbalances/" + str(ronin_address).replace('ronin:', '0x')
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/41.0.2228.0 Safari/537.36'}
        response = requests.get(url, headers=headers)

        try:
            json_data = json.loads(response.text)
        except ValueError as e:
            return {'WETH': -1, 'AXS': -1, 'SLP': -1, 'axies': -1, 'ronin_address': ronin_address}

        res = {'WETH': 0, 'AXS': 0, 'SLP': 0, 'axies': 0, 'ronin_address': ronin_address}
        for data in json_data['results']:
            if data['token_symbol'] == 'WETH':
                res['WETH'] = round(int(data['balance']) / math.pow(10, 18), 6)
            elif data['token_symbol'] == 'AXS':
                res['AXS'] = round(int(data['balance']) / math.pow(10, 18), 2)
            elif data['token_symbol'] == 'SLP':
                res['SLP'] = int(data['balance'])
            elif data['token_symbol'] == 'AXIE':
                res['axies'] = int(data['balance'])
        return res

    @staticmethod
    def get_gas_from_ethgasstation():
        r = requests.get('https://ethgasstation.info/api/ethgasAPI.json?', params={'api-key': "fd5694d64c060e4a058f34add1bf2de7df1c46f84d4381a018fe7f07c387"})
        if r.status_code == 200:
            data = r.json()
            return {'rapid': int(data['fastest'] / 10), 'fast': int(data['fast'] / 10), 'standard': int(data['average'] / 10), "slow": int(
                data['safeLow'] / 10), "rapid_wait": int(data['fastestWait'] * 60), "fast_wait": int(data['fastWait'] * 60), "standard_wait": int(
                data['avgWait'] * 60), "slow_wait": int(data['safeLowWait'] * 60)}


def setup(bot):
    bot.add_cog(CryptoCommands(bot))
