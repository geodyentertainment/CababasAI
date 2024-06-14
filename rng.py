from random import random
from os_manager import resources
from discord import Embed
from discord import Color

history:dict[str, int] = {} # For debouncing n stuff

# Stole these names from random roblox game (Sol's RNG)
RANKS = {
    'Common': 1/2, # It says 1/2, but it's really awarded when user lands on nothing
    'Uncommon': 1/4,
    'Good' : 1/10,
    'Rare': 1/16,
    'Radical': 1/31.831,
    'Crystallized': 1/64,
    'Rage': 1/128,
    'Ruby': 1/350,
    'Forbidden': 1/404,
    'Emerald': 1/500,
    'Ink': 1/700,
    'Jackpot': 1/777,
    'Sapphire': 1/800,
    'Aquamarine': 1/900,
    'Wind': 1/950,
    'Cababas Fan': 1/1000,
    'Cababas Gambler' : 1/10000
}

def roll() -> str:
    current_roll = random()
    
    for rank in reversed(RANKS):
        chance = RANKS[rank]
        if current_roll <= chance:
            return rank
    return list(RANKS.keys())[0] # Return lowest rank by default

def get_chance(rank:str) -> float:
    if rank in RANKS:
        return RANKS[rank]
    return 0

async def get_user_rank(user_id:int) -> str:
    current_rank = await resources.rng_ranks.get_rank(user_id)

    if current_rank is None:
        current_rank = list(RANKS.keys())[0]
        await resources.rng_ranks.set_rank(user_id, current_rank)
    return current_rank

async def browse_ranks(user_id:int) -> Embed:
    embed = Embed()
    embed.title = '**RNG RANKS**'
    for rank in RANKS:
        embed.add_field(
            name=f'{rank} {'⬅️' if await get_user_rank(user_id) == rank else ''}',
            value=f'{str(round(get_chance(rank)*100, 2))}%',
            inline=False
        )
    embed.colour = Color(0x006FFF)
    return embed

async def user_roll(user_id:int) -> tuple[str, bool]:
    current_rank = await get_user_rank(user_id)

    current_roll = roll()

    if (get_chance(current_rank) > get_chance(current_roll)):
        await resources.rng_ranks.set_rank(user_id, current_roll)
        return current_roll, True

    return current_roll, False