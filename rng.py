from random import random
from os_manager import resources
from discord import Embed
from discord import Color

history:dict[str, int] = {} # For debouncing n stuff

# Stole these names from random roblox game (Sol's RNG)
RANKS = {
    'Common': 1/1.95, # It says 1/2, but it's really awarded when user lands on nothing
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
    'Good Cababas': 1/1000,
    'Evil Cababas' : 1/1004,
    'Glock' : 1/1700,
    'Magnetic' : 1/2048,
    'Sidereum' : 1/4096,
    'Bleeding' : 1/4444,
    'Solar' : 1/10000
}

def roll(luck:float|None = 1.0) -> str:
    current_roll = random()
    
    temp_counter = 0.0
    
    for rank in reversed(RANKS):
        chance = RANKS[rank]
        temp_counter += (chance*luck)
        if current_roll <= temp_counter:
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

    embed.description = f'ur rank is: `{await get_user_rank(user_id)}`\n'
    
    for rank in RANKS:
        embed.add_field(
            name=f'{rank}',
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

# print(sum(RANKS.values()))

# rank = list(RANKS.keys())[0]
# counter = 0

# while rank != 'Cababas Gambler':
#     counter+=1
#     current_roll = roll()
    
#     if get_chance(current_roll) < get_chance(rank):
#         rank = current_roll
#         print(f'{rank}, {counter}')