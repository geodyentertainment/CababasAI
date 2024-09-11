import random
from discord import Client
from discord import VoiceClient
from discord import VoiceChannel
import console

def check_if_in_vc(bot:Client) -> bool:
    return (len(bot.voice_clients) > 0)

async def join(bot:Client, channel_id:int, muted:bool|None=True, deafened:bool|None=False):
    channel = bot.get_channel(channel_id)
    if channel != None:
        await channel.connect(self_mute=muted,self_deaf=deafened)
        
async def leave(bot:Client, channel_id:int|None=None):
    for vc in bot.voice_clients:
        if channel_id == None:
            try:
                vc.cleanup()
            except Exception as e:
                console.error(f'Failed to clean up voice client: {str(e)}')
            try:
                await vc.disconnect()
            except Exception as e:
                console.error(f'Failed to leave voice channel: {str(e)}')
        else:
            if (vc.channel.id == channel_id):
                try:
                    vc.cleanup()
                except Exception as e:
                    console.error(f'Failed to clean up voice client: {str(e)}')
                try:
                    await vc.disconnect()
                except Exception as e:
                    console.error(f'Failed to leave voice channel: {str(e)}')
                break
        
def get_members_in_vc_count(channel:VoiceChannel) -> int:
    count = set()
    for member in channel.members:
        count.add(member.id)
    return len(count)

def calc_chance_of_joining(total_member_count:int, voice_count:int) -> float:
    return float(voice_count)/float(total_member_count)

def calc_chance_of_leaving(total_member_count:int, voice_count:int) -> float:
    if (voice_count <= 0):
        return 1
    return (1-(float(voice_count)/float(total_member_count)))*0.1
        
async def should_join_vc(channel:VoiceChannel) -> bool:
    total_members = channel.guild.member_count
    if total_members == None:
        return False
    
    chance = calc_chance_of_joining(total_members,get_members_in_vc_count(channel=channel))
    console.log(f'{chance*100}% chance of joining {channel.name}')
    return random.random() <= chance

async def should_leave_vc(channel:VoiceChannel) -> bool:
    total_members = channel.guild.member_count
    if total_members == None:
        return True
    
    chance = calc_chance_of_leaving(total_members,get_members_in_vc_count(channel=channel))
    console.log(f'{chance*100}% chance of leaving {channel.name}')
    return random.random() <= chance