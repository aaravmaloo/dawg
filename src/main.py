import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import asyncio
import os
import json
from datetime import datetime, timezone, timedelta
import dotenv
import logging

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('dogbot')

loaded = dotenv.load_dotenv(r'C:\Users\Aarav Maloo\Desktop\dog bot\src\secret.env')
BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default(); intents.message_content = True; intents.guilds = True
bot = commands.Bot(command_prefix="!unused!", intents=intents)

DEFAULT_MIN_SPAWN_SECONDS = 120; DEFAULT_MAX_SPAWN_SECONDS = 300; DEFAULT_POST_CATCH_SPAWN_SECONDS = 30
SHIELD_DURATION_HOURS = 12; SHIELD_COST_NORMAL_DOGS = 5; THEFT_FAIL_PENALTY_NORMAL_DOGS = 5
MAX_THEFT_FAIL_STREAK_FOR_WANTED = 5; SPAWN_CATCH_BAN_HOURS_ON_WANTED_FAIL = 24
THEFT_SUCCESS_CHANCE = 0.25; SHIELD_BYPASS_CHANCE_WITH_REACTOR = 0.20
CAUGHT_DOG_EMOJI_FALLBACK = "🦴"; DOG_IMAGE_PATH_TEMPLATE = os.path.join("src", "imgs", "spawn_types", "{image_name}")
DATA_DIR = os.path.join("data")
QUESTS_FOR_CHEST = 3 
DOGSINO_ENTRY_COST_UNCOMMON_DOG_TYPE = "uncommon_dog" 
DOGSINO_ENTRY_COST_AMOUNT = 3
DOGSINO_RAREST_WIN_CHANCE = 0.01 
QUEST_RESET_HOURS = 10 
MAX_ACTIVE_QUESTS = 3

DOG_TYPES = {
    "normal_dog":    {"display_name": "Normal Dog",    "image_name": "dog.png",            "value": 10,  "spawn_weight": 2500.0, "emoji_name": "normal_dog", "emoji_id": "1384534131970412594"},
    "dog_good":      {"display_name": "Good Dog",      "image_name": "dog_good.png",       "value": 20,  "spawn_weight": 1500.0,  "emoji_name": "dog_good",   "emoji_id": "138585088318332567"},
    "dog_better":    {"display_name": "Better Dog",    "image_name": "dog_better.png",     "value": 30,  "spawn_weight": 1000.0,  "emoji_name": "dog_better", "emoji_id": "138585100167671156"},
    "uncommon_dog":  {"display_name": "Uncommon Dog",  "image_name": "uncommon_dog.png",   "value": 50,  "spawn_weight": 700.0,  "emoji_name": "uncommon_dog", "emoji_id": "138585243314525103"},
    "fine_dog":      {"display_name": "Fine Dog",      "image_name": "dog_fine.png",       "value": 70,  "spawn_weight": 500.0,  "emoji_name": "dog_fine",   "emoji_id": "1384912439040016524"},
    "loyal_dog":     {"display_name": "Loyal Dog",     "image_name": "loyal_dog.png",      "value": 100, "spawn_weight": 350.0,  "emoji_name": "loyal_dog",  "emoji_id": "138585182510429447"},
    "divine_dog":    {"display_name": "Divine Dog",    "image_name": "divine_dog.png",     "value": 150, "spawn_weight": 250.0,  "emoji_name": "divine_dog", "emoji_id": "138585112117838585"},
    "dangerous_dog": {"display_name": "Dangerous Dog", "image_name": "dangerous_dog.png",  "value": 200, "spawn_weight": 180.0,  "emoji_name": "dangerous_dog","emoji_id": "138585072151267047"},
    "angel_dog":     {"display_name": "Angel Dog",     "image_name": "angel_dog.png",      "value": 250, "spawn_weight": 120.0,   "emoji_name": "angel_dog",  "emoji_id": "138585059215907526"},
    "golden_dog":    {"display_name": "Golden Dog",    "image_name": "gold_dog.png",       "value": 300, "spawn_weight": 90.0,   "emoji_name": "gold_dog", "emoji_id": "138585167080670763"},
    "spirit_dog":    {"display_name": "Spirit Dog",    "image_name": "spirit_dog.png",     "value": 350, "spawn_weight": 70.0,   "emoji_name": "spirit_dog", "emoji_id": "138585218272697146"},
    "ancient_dog":   {"display_name": "Ancient Dog",   "image_name": "ancient_dog.png",    "value": 400, "spawn_weight": 60.0,   "emoji_name": "ancient_dog","emoji_id": "138585037708365560"},
    "super_dog":     {"display_name": "Super Dog",     "image_name": "super_dog.png",      "value": 500, "spawn_weight": 50.0,   "emoji_name": "super_dog",  "emoji_id": "138585273727801360"},
    "sonic_dog":     {"display_name": "Sonic Dog",     "image_name": "sonic_dog.png",      "value": 600, "spawn_weight": 40.0,   "emoji_name": "sonic_dog",  "emoji_id": "138585204811826623"},
    "amazing_dog":   {"display_name": "Amazing Dog",   "image_name": "amazing_dog.png",    "value": 750, "spawn_weight": 30.0,   "emoji_name": "amazing_dog","emoji_id": "138585017074254328"},
    "master_dog":    {"display_name": "Master Dog",    "image_name": "master_dog.png",     "value": 1000,"spawn_weight": 20.0,   "emoji_name": "master_dog", "emoji_id": "138585193723121452"},
    "trash_dog":     {"display_name": "Trash Dog",     "image_name": "trash_dog.png",      "value": 5,   "spawn_weight": 15.0,  "emoji_name": "trash_dog",  "emoji_id": "138585263162679541"},
    "unidentified_dog":{"display_name": "Unidentified Dog", "image_name": "unidentified_dog.jpg", "value": 1250,"spawn_weight": 8.0,    "emoji_name": "unidentified_dog","emoji_id": "138585231254283166"},
    "unbeatable_dog":{"display_name": "Unbeatable Dog","image_name": "unbeatable_dog.png", "value": 1500,"spawn_weight": 4.0,    "emoji_name": "unbeatable_dog","emoji_id": "138585254479513643"},
    "alien_dog":     {"display_name": "Alien Dog",     "image_name": "alien_dog.png",      "value": 2000,"spawn_weight": 1.5,    "emoji_name": "alien_dog",  "emoji_id": "138585005776421210"},
    "void_dog":      {"display_name": "Void Dog",      "image_name": "void_dog.png",       "value": 5000,"spawn_weight": 0.3,    "emoji_name": "void_dog",   "emoji_id": "138585292776110074"},
    "devil_dog":     {"display_name": "Devil Dog",     "image_name": "devil_dog.png",      "value": 6666,"spawn_weight": 0.08,   "emoji_name": "devil_dog",  "emoji_id": "138585127746034654"},
    "godly_dog":     {"display_name": "Godly Dog",     "image_name": "godly_dog.png",      "value": 8000,"spawn_weight": 0.02,   "emoji_name": "godly_dog",  "emoji_id": "138585147440087917"}
}
DOG_TYPE_KEYS = list(DOG_TYPES.keys()); DOG_SPAWN_KEYS_FOR_RANDOM = [key for key, props in DOG_TYPES.items() if props.get("spawn_weight", 0) > 0]
DOG_SPAWN_WEIGHTS_FOR_RANDOM = [DOG_TYPES[key]["spawn_weight"] for key in DOG_SPAWN_KEYS_FOR_RANDOM if key in DOG_SPAWN_KEYS_FOR_RANDOM]
ARC_REACTOR_TYPES = {
    "shield_piercer_charge": {"display_name": "Shield Piercer Charge", "description": "One-time 25% shield bypass. Consumed on /steal.", "duration_seconds": 0, "emoji": "💥", "effect_type": "shield_bypass_on_steal"},
    "amulet_of_duplication": {"display_name": "Amulet of Duplication", "description": f"For 12 hours, every dog caught becomes two!", "duration_seconds": 12 * 3600, "emoji": "♊", "effect_type": "double_catch"},
    "charm_of_thieves_luck": {"display_name": "Charm of Thieves' Luck", "description": "For 1 hour, +15% theft success chance.", "duration_seconds": 1 * 3600, "emoji": "🍀", "effect_type": "theft_boost"},
    "magnet_of_attraction": {"display_name": "Magnet of Attraction", "description": "For 15 minutes, you feel a stronger pull from spawning dogs (conceptual).", "duration_seconds": 15 * 60, "emoji": "🧲", "effect_type": "personal_lure"},
    "cooldown_reducer": {"display_name": "Cooldown Reducer", "description": "Instantly reduces this server's next dog spawn cooldown by up to 10 minutes.", "duration_seconds": 0, "emoji": "⏱️", "effect_type": "spawn_cooldown_reduction"}
}
ARC_REACTOR_TYPE_KEYS = list(ARC_REACTOR_TYPES.keys()); active_dog_spawns = {}
ACHIEVEMENTS = {
    "first_catch": {"name": "First Catch!", "description": "You caught your very first dog!", "emoji": "🎉"},
    "dog_novice": {"name": "Dog Novice", "description": "Collect 10 dogs in total.", "emoji": "🐾"},
    "dog_collector": {"name": "Dog Collector", "description": "Collect 50 dogs in total.", "emoji": "🏆"},
    "normal_dog_expert": {"name": "Normal Dog Expert", "description": f"Collect 25 Normal Dogs.", "emoji": DOG_TYPES.get("normal_dog",{}).get("emoji_name", "🐶")}, # Using normal_dog key
    "rare_find": {"name": "Rare Find", "description": "Catch a dog with a value of 1000 or more.", "emoji": "💎"},
    "variety_lover": {"name": "Variety Lover", "description": "Own at least 10 different types of dogs.", "emoji": "🌈"},
    "pack_leader": {"name": "Pack Leader", "description": "Own at least 20 dogs of 5 different types.", "emoji": "👑"},
    "dog_millionaire": {"name": "Dog Millionaire", "description": "Reach a total dog collection value of 1,000,000.", "emoji": "💰"},
    "dedicated_catcher": {"name": "Dedicated Catcher", "description": "Catch 100 dogs.", "emoji": "🎣"},
    "master_crafter": {"name": "Master Crafter", "description": "Successfully craft 10 items (dogs or reactors).", "emoji": "🛠️"}
}
ACHIEVEMENT_KEYS = list(ACHIEVEMENTS.keys())
QUEST_DEFINITIONS = {
    "catch_normals_1": {"id": "catch_normals_1", "title": "Basic Training", "description": "Catch 5 Normal Dogs.", "objective_type": "catch_specific", "dog_type_key": "normal_dog", "target_count": 5, "reward_type": "dogs", "reward_item_key": "dog_good", "reward_amount": 2, "xp_reward": 50},
    "catch_any_1": {"id": "catch_any_1", "title": "Getting Started", "description": "Catch any 3 dogs.", "objective_type": "catch_any", "target_count": 3, "reward_type": "dogs", "reward_item_key": "uncommon_dog", "reward_amount": 1, "xp_reward": 30},
    "value_milestone_1": {"id": "value_milestone_1", "title": "Small Fortune", "description": "Reach a total dog collection value of 500.", "objective_type": "total_value", "target_value": 500, "reward_type": "dogs", "reward_item_key": "fine_dog", "reward_amount": 1, "xp_reward": 100},
    "catch_uncommon_1": {"id": "catch_uncommon_1", "title": "Beyond the Basics", "description": "Catch 2 Uncommon Dogs.", "objective_type": "catch_specific", "dog_type_key": "uncommon_dog", "target_count": 2, "reward_type": "dogs", "reward_item_key": "loyal_dog", "reward_amount": 1, "xp_reward": 75},
    "craft_item_1": {"id": "craft_item_1", "title": "Budding Crafter", "description": "Craft any 1 item (dog or reactor).", "objective_type": "craft_any", "target_count": 1, "reward_type": "arc_reactors", "reward_item_key": "charm_of_thieves_luck", "reward_amount": 1, "xp_reward": 60}
}

@bot.event
async def on_message(msg:discord.Message):
    if msg.author==bot.user or not msg.guild or not msg.content:
        return

    if msg.content.lower()=="dog":
        channel_id_typed_in = msg.channel.id
        guild_id_typed_in = str(msg.guild.id)
        
        logger.info(f"'dog' typed by {msg.author.name} in channel {channel_id_typed_in} (Guild: {msg.guild.name}).")
        logger.debug(f"Current active_dog_spawns state: {active_dog_spawns}")

        spawn_info = active_dog_spawns.get(channel_id_typed_in)
        logger.debug(f"s_info for channel {channel_id_typed_in}: {spawn_info}")

        if spawn_info and str(spawn_info.get("guild_id")) == guild_id_typed_in:
            logger.info(f"Valid dog spawn found for channel {channel_id_typed_in}. Proceeding with catch for {msg.author.name}.")
            
            # Store info before deleting from active_dog_spawns
            dog_type_key_from_spawn = spawn_info["dog_type_key"] # Use this for consistency
            guild_id_from_spawn = str(spawn_info["guild_id"]) # Ensure string
            original_spawn_message_id = spawn_info.get("message_id")
            spawn_timestamp = spawn_info.get("spawn_timestamp")
            
            # Attempt to "claim" this catch
            if channel_id_typed_in in active_dog_spawns:
                del active_dog_spawns[channel_id_typed_in]
                logger.info(f"CATCH EVENT: '{msg.author.name}' successfully claimed dog '{dog_type_key_from_spawn}' from channel {channel_id_typed_in}.")
            else:
                logger.info(f"CATCH INFO: Dog in channel {channel_id_typed_in} was ALREADY claimed when {msg.author.name}'s attempt was processed.")
                return 

            try:
                time_taken_str = "" # Initialize ts_str as time_taken_str
                if spawn_timestamp:
                    catch_timestamp = int(datetime.now(timezone.utc).timestamp())
                    time_taken_seconds = catch_timestamp - spawn_timestamp
                    time_taken_str = f" in **{format_time_delta(time_taken_seconds)}**"
                
                guild_data = load_guild_data(guild_id_from_spawn, msg.guild.name)
                user_data = get_user_data_block(guild_id_from_spawn, str(msg.author.id), guild_data)
                user_dog_inventory = user_data["inventory"]
                
                dogs_to_add = 1
                active_effects = user_data.get("active_effects", {})
                current_time_for_effects = int(datetime.now(timezone.utc).timestamp())
                if active_effects.get("double_catch_until", 0) > current_time_for_effects:
                    dogs_to_add = 2
                    logger.info(f"Double catch active for {msg.author.name}!")
                
                user_dog_inventory[dog_type_key_from_spawn]=user_dog_inventory.get(dog_type_key_from_spawn,0) + dogs_to_add
                
                current_catch_process_time = int(datetime.now(timezone.utc).timestamp())
                post_catch_delay = guild_data["settings"].get("post_catch_spawn_seconds",DEFAULT_POST_CATCH_SPAWN_SECONDS)
                guild_data["spawn_state"]["next_eligible_spawn_timestamp"]=current_catch_process_time + post_catch_delay
                guild_data["spawn_state"]["is_in_post_catch_cooldown"]=True
                
                save_guild_data(guild_id_from_spawn, guild_data, msg.guild.name) 
                
                await update_quest_progress(msg, str(msg.author.id), guild_id_from_spawn, "catch", {"dog_type_key": dog_type_key_from_spawn})
                
                dog_info_display = DOG_TYPES[dog_type_key_from_spawn]
                emoji_id_display = dog_info_display.get("emoji_id")
                emoji_name_display = dog_info_display.get("emoji_name")
                emoji_str_display = f"<:{emoji_name_display}:{emoji_id_display}>" if emoji_id_display and emoji_name_display else CAUGHT_DOG_EMOJI_FALLBACK
                
                catch_msg_extra_display = " (x2!)" if dogs_to_add > 1 else ""
                await msg.channel.send(f"Caught by {msg.author.mention}: **{dog_info_display['display_name']}**{catch_msg_extra_display}{time_taken_str}! {emoji_str_display}")
                
                if original_spawn_message_id:
                    try:
                        original_msg_obj = await msg.channel.fetch_message(original_spawn_message_id)
                        await original_msg_obj.delete()
                        logger.info(f"Deleted original spawn message (ID: {original_spawn_message_id}).")
                    except Exception as e_del: logger.info(f"Could not delete original spawn message (ID: {original_spawn_message_id}): {e_del}")

            except KeyError as ke:
                logger.error(f"CATCH CRITICAL KeyError: Dog type key '{dog_type_key_from_spawn}' (from spawn_info) not found in DOG_TYPES. Error: {ke}")
                await msg.channel.send("Woof! A very strange error occurred with this dog's type. Please report this.")
            except Exception as e:
                logger.error(f"CATCH EVENT Unhandled Error: {e}")
                import traceback; traceback.print_exc()
                await msg.channel.send("Woof! Something went very wrong with your catch! Please try again or report this.")

def format_time_delta(seconds: int) -> str:
    if seconds < 0: seconds = 0
    if seconds == 1: return "1 second"
    if seconds < 60: return f"{seconds} seconds"
    
    parts = []
    
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if days > 0: parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0: parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0: parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not parts : parts.append(f"{seconds} second{'s' if seconds != 1 else ''}") # Add seconds if it's the only unit or > 0

    if not parts: return "0 seconds" # Should only happen if input was 0 initially
    if len(parts) == 1: return parts[0]
    
    # Join with 'and' before the last element
    return ", ".join(parts[:-1]) + " and " + parts[-1]

def get_guild_data_file_path(gid): return os.path.join(DATA_DIR, f"guild_{gid}.json")
def _get_default_user_data_structure():
    return {"inventory": {key: 0 for key in DOG_TYPE_KEYS}, "arc_reactors": {key: 0 for key in ARC_REACTOR_TYPE_KEYS}, "active_effects": {}, "shield_active_until": 0, "theft_fail_streak": 0, "wanted_level": False, "spawn_catch_banned_until": 0, "unlocked_achievements": [], "active_quests": {}, "completed_quests_this_cycle": [], "last_quest_reset_timestamp":0, "quests_completed_for_chest": 0, "chest_available": False }
def load_guild_data(gid: str, gname: str = "?") -> dict:
    path = get_guild_data_file_path(gid); ts = int(datetime.now(timezone.utc).timestamp())
    min_dfns = DEFAULT_MIN_SPAWN_SECONDS; id_new = random.randint(min(10, min_dfns//2 if min_dfns>20 else 10), min_dfns)
    guild_file_df = {"settings":{"min_spawn_seconds":min_dfns,"max_spawn_seconds":DEFAULT_MAX_SPAWN_SECONDS,"post_catch_spawn_seconds":DEFAULT_POST_CATCH_SPAWN_SECONDS,"server_name_for_reference":gname,"crafting_enabled":True,"theft_enabled":True,"quests_enabled":True, "spawn_channel_ids": []},"spawn_state":{"next_eligible_spawn_timestamp":ts+id_new,"is_in_post_catch_cooldown":False},"crafting_recipes":{"dogs":{},"arc_reactors":{}}, "user_data":{}}
    if not os.path.exists(path): return guild_file_df
    try:
        with open(path,'r')as f:c=f.read()
        if not c.strip(): return guild_file_df
        data=json.loads(c)
        for tk,tv in guild_file_df.items():
            dt=data.setdefault(tk,tv.copy()if isinstance(tv,(dict,list))else tv)
            if isinstance(tv,dict)and tk!="user_data":
                for sk,sv in tv.items():
                    if isinstance(dt,dict):dt.setdefault(sk,sv.copy()if isinstance(sv,(dict,list))else sv)
        all_users_data = data.setdefault("user_data", {})
        if isinstance(all_users_data, dict):
            for uid_str, u_block_loaded in list(all_users_data.items()):
                def_usr_struct = _get_default_user_data_structure()
                if not isinstance(u_block_loaded, dict): all_users_data[uid_str] = def_usr_struct.copy(); continue
                for prop_k, def_prop_v in def_usr_struct.items(): u_block_loaded.setdefault(prop_k, def_prop_v.copy() if isinstance(def_prop_v, (dict, list)) else def_prop_v)
                inv = u_block_loaded.setdefault("inventory", {}); reac = u_block_loaded.setdefault("arc_reactors", {})
                for dog_k_e in DOG_TYPE_KEYS: inv.setdefault(dog_k_e, 0)
                for reac_k_e in ARC_REACTOR_TYPE_KEYS: reac.setdefault(reac_k_e, 0)
                u_block_loaded.setdefault("completed_quests_this_cycle", []) # Ensure this exists
        else: data["user_data"] = {}
        s_state=data.setdefault("spawn_state",guild_file_df["spawn_state"].copy())
        if s_state.get("next_eligible_spawn_timestamp",0)==0 or s_state.get("next_eligible_spawn_timestamp",ts)<ts-(7*24*3600):
            min_s_res=data.get("settings",{}).get("min_spawn_seconds",DEFAULT_MIN_SPAWN_SECONDS); res_delay=random.randint(min(10,min_s_res//2 if min_s_res>20 else 10),min_s_res)
            s_state["next_eligible_spawn_timestamp"]=ts+res_delay
        data.setdefault("settings", {}).setdefault("spawn_channel_ids", [])
        return data
    except Exception as e:
        logger.error(f"Err load guild {gid}: {e}")
        print(f"Err load guild {gid}:{e}");import traceback;traceback.print_exc();
        return guild_file_df
def save_guild_data(gid,d,gname=""):
    if not os.path.exists(DATA_DIR):
        try:os.makedirs(DATA_DIR)
        except Exception as e:logger.error(f"Err creating data dir for save: {e}");print(f"Err creating data dir for save: {e}");return False
    if gname:d.setdefault("settings",{}).update({"server_name_for_reference":gname})
    d.setdefault("settings",{}); d["settings"].setdefault("spawn_channel_ids", [])
    d.setdefault("spawn_state",{});d.setdefault("crafting_recipes",{"dogs":{}, "arc_reactors":{}});d.setdefault("user_data",{})
    try:
        with open(get_guild_data_file_path(gid),'w')as f:json.dump(d,f,indent=4);return True
    except Exception as e:logger.error(f"Err save guild {gid} data:{e}");print(f"Err save guild {gid} data:{e}");return False
def get_user_data_block(gid: str, uid: str, guild_data_ref: dict) -> dict:
    uid_s = str(uid); all_users_data = guild_data_ref.setdefault("user_data", {})
    if uid_s not in all_users_data or not isinstance(all_users_data[uid_s], dict): all_users_data[uid_s] = _get_default_user_data_structure()
    else:
        user_block = all_users_data[uid_s]; default_user_struct_template = _get_default_user_data_structure()
        for key, default_value in default_user_struct_template.items(): user_block.setdefault(key, default_value.copy() if isinstance(default_value, (dict, list)) else default_value)
        inv = user_block.setdefault("inventory", {}); reac = user_block.setdefault("arc_reactors", {})
        for dog_key in DOG_TYPE_KEYS: inv.setdefault(dog_key, 0)
        for reactor_key in ARC_REACTOR_TYPE_KEYS: reac.setdefault(reactor_key, 0)
        user_block.setdefault("completed_quests_this_cycle",[])
    return all_users_data[uid_s]

async def update_quest_progress(source_event, user_id: str, guild_id: str, event_type: str, event_data: dict = None):
    if event_data is None:
        event_data = {}
    logger.info(f"QUEST_UPDATE: User {user_id} in Guild {guild_id} - Event: '{event_type}', Data: {event_data}")
    guild_data = load_guild_data(guild_id)
    user_data = get_user_data_block(guild_id, user_id, guild_data)
    active_quests = user_data.setdefault("active_quests", {})
    completed_this_cycle = user_data.setdefault("completed_quests_this_cycle", [])
    quests_to_remove_from_active = []
    newly_completed_titles_for_chat = []
    guild_modified_by_progress = False

    for quest_id, quest_prog_data in list(active_quests.items()):
        quest_def = QUEST_DEFINITIONS.get(quest_id)
        if not quest_def:
            logger.warning(f"Orphaned active quest '{quest_id}' for user {user_id}.")
            continue
        original_progress = quest_prog_data.get("progress", 0)
        current_progress = original_progress
        target = quest_def.get("target_count", quest_def.get("target", 1))
        made_progress_this_event = False

        # --- CATCH SPECIFIC ---
        if event_type == "catch" and quest_def.get("objective_type") == "catch_specific":
            if event_data.get("dog_type_key") == quest_def.get("dog_type_key"):
                current_progress += 1
                made_progress_this_event = True
        # --- CATCH ANY ---
        if event_type == "catch" and quest_def.get("objective_type") == "catch_any":
            current_progress += 1
            made_progress_this_event = True
        # --- CATCH VARIETY ---
        if event_type == "catch" and quest_def.get("objective_type") == "catch_variety":
            caught_dog_key = event_data.get("dog_type_key")
            if caught_dog_key:
                caught_variety_list = quest_prog_data.setdefault("caught_variety", [])
                if caught_dog_key not in caught_variety_list:
                    caught_variety_list.append(caught_dog_key)
                    current_progress = len(caught_variety_list)
                    made_progress_this_event = True
        # --- TOTAL VALUE ---
        if quest_def.get("objective_type") == "total_value":
            user_inventory = user_data.get("inventory", {})
            calculated_total_value = sum(DOG_TYPES.get(dk, {}).get("value", 0) * dc for dk, dc in user_inventory.items() if dk in DOG_TYPES)
            if calculated_total_value != current_progress:
                current_progress = calculated_total_value
                made_progress_this_event = True
        # --- CATCH VALUE GTE ---
        if event_type == "catch" and quest_def.get("objective_type") == "catch_value_gte":
            caught_dog_key = event_data.get("dog_type_key")
            if caught_dog_key and DOG_TYPES.get(caught_dog_key, {}).get("value", 0) >= quest_def.get("target_value", float('inf')):
                current_progress += 1
                made_progress_this_event = True
        # --- CRAFT ANY ---
        if event_type == "craft" and quest_def.get("objective_type") == "craft_any":
            current_progress += 1
            made_progress_this_event = True

        if made_progress_this_event:
            quest_prog_data["progress"] = current_progress
            guild_modified_by_progress = True
        if current_progress >= target:
            if quest_id not in completed_this_cycle:
                completed_this_cycle.append(quest_id)
                newly_completed_titles_for_chat.append(quest_def["title"])
                guild_modified_by_progress = True
            if quest_id not in quests_to_remove_from_active:
                quests_to_remove_from_active.append(quest_id)
            # Give reward
            reward_type = quest_def.get("reward_type")
            reward_item_key = quest_def.get("reward_item_key")
            reward_amount = quest_def.get("reward_amount", 1)
            inv_to_upd = user_data.setdefault("inventory", {k: 0 for k in DOG_TYPE_KEYS})
            reac_to_upd = user_data.setdefault("arc_reactors", {k: 0 for k in ARC_REACTOR_TYPE_KEYS})
            if reward_type == "dogs" and reward_item_key in DOG_TYPES:
                inv_to_upd[reward_item_key] = inv_to_upd.get(reward_item_key, 0) + reward_amount
            elif reward_type == "arc_reactors" and reward_item_key in ARC_REACTOR_TYPES:
                reac_to_upd[reward_item_key] = reac_to_upd.get(reward_item_key, 0) + reward_amount
    if quests_to_remove_from_active:
        for qid_done in quests_to_remove_from_active:
            if qid_done in active_quests:
                del active_quests[qid_done]
            user_data.setdefault("completed_quests_lifetime", []).append(qid_done)
        guild_modified_by_progress = True
    if guild_modified_by_progress:
        save_guild_data(guild_id, guild_data)
    if newly_completed_titles_for_chat:
        user_object_chat = None
        channel_to_send_chat = None
        if hasattr(source_event, 'guild') and source_event.guild is not None:
            user_object_chat = source_event.guild.get_member(int(user_id))
        if hasattr(source_event, 'channel') and source_event.channel is not None:
            channel_to_send_chat = source_event.channel
        if user_object_chat and channel_to_send_chat:
            try:
                completed_titles_str_chat = ", ".join([f"**{title}**" for title in newly_completed_titles_for_chat])
                await channel_to_send_chat.send(f"📜 {user_object_chat.mention} just completed quest(s): {completed_titles_str_chat}!")
            except Exception as e_chat_notify:
                logger.error(f"Error sending quest completion chat notification: {e_chat_notify}")
    await check_achievements_and_chest(source_event, user_id, guild_id, "quest_progress_update", {})

# --- QUEST DEFINITIONS (Example) ---
QUEST_DEFINITIONS = {
    "catch_normals_basic": {"id": "catch_normals_basic", "title": "Normal Dog Roundup", "description": "Catch 3 Normal Dogs.", "objective_type": "catch_specific", "dog_type_key": "normal_dog", "target_count": 3, "reward_type": "dogs", "reward_item_key": "dog_good", "reward_amount": 1},
    "catch_any_starter": {"id": "catch_any_starter", "title": "First Steps", "description": "Catch any 2 dogs.", "objective_type": "catch_any", "target_count": 2, "reward_type": "dogs", "reward_item_key": "uncommon_dog", "reward_amount": 1},
    "craft_something_simple": {"id": "craft_something_simple", "title": "Tinkerer", "description": "Craft any 1 item.", "objective_type": "craft_any", "target_count": 1, "reward_type": "arc_reactors", "reward_item_key": "charm_of_thieves_luck", "reward_amount": 1}, # Assuming charm_of_thieves_luck is a reactor key
    "value_hunter": {"id": "value_hunter", "title": "Value Hunter", "description": "Catch a dog worth at least 500 value.", "objective_type": "catch_value_gte", "target_value": 500, "reward_type": "dogs", "reward_item_key": "fine_dog", "reward_amount": 2},
    "variety_catcher": {"id": "variety_catcher", "title": "Variety Catcher", "description": "Catch 3 different types of dogs.", "objective_type": "catch_variety", "target_count": 3, "reward_type": "dogs", "reward_item_key": "loyal_dog", "reward_amount": 1},
}

@bot.event
async def on_ready():
    logger.info(f"ON_READY: '{bot.user.name}' connected! (ID: {bot.user.id})")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Created data directory at {DATA_DIR}")
    for g in bot.guilds:
        gd = load_guild_data(g.id, g.name)
        save_guild_data(g.id, gd, g.name)
        logger.info(f"Loaded and saved data for guild: {g.name} ({g.id})")
    try:
        synced = await bot.tree.sync()
        logger.info(f"ON_READY: Synced {len(synced)} commands: {[cmd.name for cmd in synced]}")
        print(f"ON_READY: Synced {len(synced)} commands: {[cmd.name for cmd in synced]}")
    except Exception as e:
        logger.error(f"ON_READY: Error syncing commands: {e}")
    
    for g in bot.guilds:
        gd = load_guild_data(g.id, g.name)
        spawn_channels = gd.get('settings', {}).get('spawn_channel_ids', [])
        logger.info(f"Guild: {g.name} ({g.id}) | Spawn Channels: {spawn_channels}")
        for ch_id in spawn_channels:
            ch = g.get_channel(ch_id)
            logger.info(f"  - Channel: {ch.name if ch else 'N/A'} ({ch_id})")
    if not per_guild_spawn_checker_task.is_running():
        per_guild_spawn_checker_task.start()
        logger.info("Started per_guild_spawn_checker_task loop.")
    if not clear_expired_effects_task.is_running():
        clear_expired_effects_task.start()
        logger.info("Started clear_expired_effects_task loop.")
    if not quest_reset_task.is_running():
        quest_reset_task.start()
        logger.info("Started quest_reset_task loop.")
    logger.info("Bot is fully ready and all background tasks are running.")

@tasks.loop(minutes=2)
async def log_guild_status_task():
    logger.info("--- Guild/Spawn Status ---")
    for g in bot.guilds:
        gd = load_guild_data(g.id, g.name)
        spawn_channels = gd.get('settings', {}).get('spawn_channel_ids', [])
        next_spawn = gd.get('spawn_state', {}).get('next_eligible_spawn_timestamp', 0)
        logger.info(f"Guild: {g.name} ({g.id}) | Spawn Channels: {spawn_channels} | Next Spawn: {datetime.fromtimestamp(next_spawn, timezone.utc) if next_spawn else 'N/A'}")
        for ch_id in spawn_channels:
            ch = g.get_channel(ch_id)
            logger.info(f"  - Channel: {ch.name if ch else 'N/A'} ({ch_id})")
    logger.info("-------------------------")

@tasks.loop(seconds=15)
async def per_guild_spawn_checker_task():
    ts = int(datetime.now(timezone.utc).timestamp())
    for g in bot.guilds:
        gd = load_guild_data(str(g.id), g.name)
        s = gd["settings"]
        ss = gd["spawn_state"]
        allowed_spawn_channel_ids = s.get("spawn_channel_ids", [])
        if not allowed_spawn_channel_ids:
            continue
        if ts >= ss.get("next_eligible_spawn_timestamp", 0):
            # Pick a random eligible channel
            potential_channels = [
                c for c in [g.get_channel(cid) for cid in allowed_spawn_channel_ids]
                if c and isinstance(c, discord.TextChannel) and c.permissions_for(g.me).send_messages
            ]
            if not potential_channels:
                continue
            ch = random.choice(potential_channels)
            # Pick a random dog type
            dog_key = random.choices(DOG_SPAWN_KEYS_FOR_RANDOM, weights=DOG_SPAWN_WEIGHTS_FOR_RANDOM, k=1)[0]
            di = DOG_TYPES[dog_key]
            img_path = DOG_IMAGE_PATH_TEMPLATE.format(image_name=di["image_name"])
            msg_text = f"A wild **{di['display_name']}** has appeared! Type `dog` to catch it!"
            try:
                file = discord.File(img_path) if os.path.exists(img_path) else None
                s_msg = await ch.send(msg_text, file=file) if file else await ch.send(msg_text)
                active_dog_spawns[ch.id] = {
                    "dog_type_key": dog_key,
                    "guild_id": g.id,
                    "message_id": s_msg.id,
                    "spawn_timestamp": ts
                }
                # Set next eligible spawn time
                ss["next_eligible_spawn_timestamp"] = ts + random.randint(DEFAULT_MIN_SPAWN_SECONDS, DEFAULT_MAX_SPAWN_SECONDS)
                ss["is_in_post_catch_cooldown"] = False
                save_guild_data(str(g.id), gd, g.name)
            except Exception as e:
                logger.error(f"Error spawning dog in {g.name}: {e}")

# --- CLEAR EXPIRED EFFECTS TASK ---
@tasks.loop(minutes=5)
async def clear_expired_effects_task():
    now_ts = int(datetime.now(timezone.utc).timestamp())
    for g in bot.guilds:
        guild_data = load_guild_data(str(g.id), g.name)
        user_data_all = guild_data.get("user_data", {})
        changed = False
        for uid, user_data in user_data_all.items():
            active_effects = user_data.get("active_effects", {})
            expired_keys = [k for k, v in active_effects.items() if isinstance(v, int) and v < now_ts]
            for k in expired_keys:
                active_effects.pop(k, None)
                changed = True
        if changed:
            save_guild_data(str(g.id), guild_data, g.name)

@tasks.loop(hours=QUEST_RESET_HOURS)
async def quest_reset_task():
    """Periodically resets quests for all users in all guilds."""
    now = int(datetime.now(timezone.utc).timestamp())
    for g in bot.guilds:
        gd = load_guild_data(str(g.id), g.name)
        changed = False
        for uid, udata in gd.get("user_data", {}).items():
            # Only reset if enough time has passed
            last_reset = udata.get("last_quest_reset_timestamp", 0)
            if now - last_reset >= QUEST_RESET_HOURS * 3600:
                udata["active_quests"] = {}
                udata["completed_quests_this_cycle"] = []
                udata["last_quest_reset_timestamp"] = now
                changed = True
        if changed:
            save_guild_data(str(g.id), gd, g.name)

# --- PLACEHOLDER: Define missing async function for achievements and chest check ---
async def check_achievements_and_chest(source_event, user_id, guild_id, event_type, event_data=None):
    if event_data is None:
        event_data = {}
    guild_data = load_guild_data(guild_id)
    user_data = get_user_data_block(guild_id, user_id, guild_data)
    # --- Chest Awarding Logic ---
    if len(user_data.get("completed_quests_this_cycle", [])) >= QUESTS_FOR_CHEST:
        if not user_data.get("chest_available", False):
            user_data["chest_available"] = True
            user_data["completed_quests_this_cycle"] = []
            save_guild_data(guild_id, guild_data)
            # Notify user
            user_object = None
            channel_to_send = None
            if hasattr(source_event, 'guild') and source_event.guild is not None:
                user_object = source_event.guild.get_member(int(user_id))
            if hasattr(source_event, 'channel') and source_event.channel is not None:
                channel_to_send = source_event.channel
            msg = f"🎁 {user_object.mention if user_object else ''} You've completed enough quests and earned a **Dog Chest**! Use `/chest open` to claim your reward."
            if channel_to_send and user_object:
                try:
                    await channel_to_send.send(msg)
                except Exception:
                    pass
            elif user_object:
                try:
                    await user_object.send(msg)
                except Exception:
                    pass

# --- CHEST COMMAND ---
@bot.tree.command(name="chest", description="Open your Dog Chest if you have one!")
@app_commands.describe(action="Action to perform with your chest.")
@app_commands.choices(action=[app_commands.Choice(name="Open Chest", value="open")])
async def chest_slash(interaction: discord.Interaction, action: str = "open"):
    if not interaction.guild:
        await interaction.response.send_message("Server only.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    uid = str(interaction.user.id)
    guild_data = load_guild_data(gid, interaction.guild.name)
    user_data = get_user_data_block(gid, uid, guild_data)
    if not user_data.get("chest_available", False):
        await interaction.response.send_message("You don't have a Dog Chest to open yet! Complete more quests.", ephemeral=True)
        return
    # Give a random dog as a reward (customize as you wish)
    reward_key = random.choices(DOG_SPAWN_KEYS_FOR_RANDOM, weights=DOG_SPAWN_WEIGHTS_FOR_RANDOM, k=1)[0]
    user_data["inventory"][reward_key] = user_data["inventory"].get(reward_key, 0) + 1
    user_data["chest_available"] = False
    save_guild_data(gid, guild_data, interaction.guild.name)
    di = DOG_TYPES[reward_key]
    en, ei = di.get("emoji_name"), di.get("emoji_id")
    emo = f"<:{en}:{ei}>" if en and ei else "🦴"
    await interaction.response.send_message(f"🎁 You opened a Dog Chest and found: {emo} **{di['display_name']}**! Congratulations!", ephemeral=False)

# --- IMPROVED QUESTS UI ---
@bot.tree.command(name="quests", description="View your current active quests.")
async def quests_view_slash(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("Server only.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    uid = str(interaction.user.id)
    guild_data = load_guild_data(gid, interaction.guild.name)
    user_data = get_user_data_block(gid, uid, guild_data)
    active_quests = user_data.get("active_quests", {})
    completed_quests = set(user_data.get("completed_quests_this_cycle", []))
    embed = discord.Embed(title=f"📜 {interaction.user.display_name}'s Active Quests", color=discord.Color.dark_purple())
    quest_lines = []
    for quest_id, prog_data in active_quests.items():
        quest_def = QUEST_DEFINITIONS.get(quest_id)
        if not quest_def:
            continue
        progress = prog_data.get("progress", 0)
        target = quest_def.get("target_count", quest_def.get("target", 1))
        is_done = progress >= target or quest_id in completed_quests
        check = "✅" if is_done else "⬜"
        # Progress bar
        bar_length = 12
        filled = int(min(progress / target, 1.0) * bar_length) if target > 0 else bar_length
        bar = "🟩" * filled + "⬜" * (bar_length - filled)
        quest_lines.append(f"{check} **{quest_def['title']}**\n{quest_def['description']}\nProgress: {progress}/{target} {bar}")
    if not quest_lines:
        embed.description = "You have no active quests. New quests are assigned roughly every 10 hours!"
    else:
        embed.description = "\n\n".join(quest_lines)
    # Chest status
    if user_data.get("chest_available", False):
        embed.add_field(name="🎁 Dog Chest Ready!", value="Use `/chest open` to claim your reward!", inline=False)
    last_reset_ts = user_data.get("last_quest_reset_timestamp", 0)
    next_reset_ts = last_reset_ts + (QUEST_RESET_HOURS * 3600)
    current_ts = int(datetime.now(timezone.utc).timestamp())
    if next_reset_ts > current_ts:
        time_to_reset = next_reset_ts - current_ts
        embed.set_footer(text=f"New quests available in: {format_time_delta(time_to_reset)}")
    else:
        embed.set_footer(text=f"Quest reset period is active. New quests should appear soon!")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- SLASH COMMANDS ---
# (inventory, achievements, leaderboard, catalogue, setup, all crafting, shield, steal, givedog, forcespawn, chest, dogsino)
# The full definitions of previously working commands should be placed here.
# I will include the newly added/modified ones: inventory, achievements, chest, dogsino, quests view.

@bot.tree.command(name="inventory", description="Shows your collection and stats.")
@app_commands.describe(user="The user whose inventory you want to see (optional, defaults to yourself).")
async def inventory_slash(interaction:discord.Interaction,user:discord.Member=None):
    target_user = user if user else interaction.user
    if not interaction.guild:await interaction.response.send_message("Srv only.",ephemeral=True);return
    await interaction.response.defer(ephemeral=False)
    guild_data_loaded = load_guild_data(str(interaction.guild.id), interaction.guild.name)
    user_data_block = get_user_data_block(str(interaction.guild.id), str(target_user.id), guild_data_loaded)
    user_dog_inventory = user_data_block["inventory"]; user_arc_reactors = user_data_block.get("arc_reactors", {}); unlocked_ach_keys = user_data_block.get("unlocked_achievements", [])
    shield_until = user_data_block.get("shield_active_until", 0); current_time = int(datetime.now(timezone.utc).timestamp())
    is_empty_dogs = not user_dog_inventory or all(c==0 for c in user_dog_inventory.values())
    is_empty_reactors = not user_arc_reactors or all(c==0 for c in user_arc_reactors.values())
    if is_empty_dogs and is_empty_reactors and not unlocked_ach_keys : msg="Your profile is quite empty!" if target_user == interaction.user else f"{target_user.display_name}'s profile is quite empty."; await interaction.followup.send(msg); return
    total_collection_value = 0; total_dog_count = 0
    if not is_empty_dogs:
        for dog_key, count in user_dog_inventory.items():
            if dog_key in DOG_TYPES and count > 0: total_collection_value += DOG_TYPES[dog_key].get("value", 0) * count; total_dog_count += count
    emb=discord.Embed(title=f"{target_user.display_name}", color=discord.Color.random())
    if target_user.avatar: emb.set_thumbnail(url=target_user.avatar.url)
    summary_lines = [f"🐕 Total Dogs: **{total_dog_count}** | Collection Value: **{total_collection_value}** ✨"]
    if shield_until > current_time: summary_lines.append(f"🛡️ Shield: Active (expires {discord.utils.format_dt(datetime.fromtimestamp(shield_until, timezone.utc), style='R')})")
    else: summary_lines.append(f"🛡️ Shield: Inactive")
    summary_lines.append(f"🏆 Achievements: **{len(unlocked_ach_keys)}/{len(ACHIEVEMENTS)}**")
    emb.description = "\n".join(summary_lines)
    if not is_empty_dogs:
        s_inv=sorted([(k,v)for k,v in user_dog_inventory.items() if v>0 and k in DOG_TYPES],key=lambda i:DOG_TYPES[i[0]].get("value",0),reverse=False)
        dog_field_value = ""
        for dk,c in s_inv:
            di=DOG_TYPES.get(dk);
            if not di: continue
            e_name,e_id=di.get("emoji_name"),di.get("emoji_id")
            fn=f"<:{e_name}:{e_id}> "if e_name and e_id else"❓ ";fn+=f"**{di['display_name']}**: {c}"
            dog_field_value += fn + "\n"
        if dog_field_value: emb.add_field(name="--- Dog Collection ---", value=dog_field_value.strip(), inline=False)
    if not is_empty_reactors:
        reactor_field_value = "\n".join([f"{ARC_REACTOR_TYPES[rk].get('emoji','⚙️')} **{ARC_REACTOR_TYPES[rk]['display_name']}**: {count}" for rk, count in user_arc_reactors.items() if count > 0 and rk in ARC_REACTOR_TYPES])
        if reactor_field_value: emb.add_field(name="--- Arc Reactors ---", value=reactor_field_value, inline=False)
    if not emb.fields and (emb.description == "\n".join(summary_lines) and is_empty_dogs and is_empty_reactors) : emb.description += "\n\nNothing else to show."
    await interaction.followup.send(embed=emb)
@inventory_slash.error
async def inventory_slash_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f"Error in /inventory: {error}");
    if hasattr(error, 'original'): import traceback; traceback.print_exception(type(error.original), error.original, error.original.__traceback__)
    if not interaction.response.is_done(): await interaction.response.send_message("Error fetching inventory.", ephemeral=True)
    else: await interaction.followup.send("Error fetching inventory.", ephemeral=True)

@bot.tree.command(name="achievements", description="View unlocked achievements for a user.")
@app_commands.describe(user="The user whose achievements you want to see (optional, defaults to yourself).")
async def achievements_slash(interaction: discord.Interaction, user: discord.Member = None):
    target_user = user if user else interaction.user
    if not interaction.guild: await interaction.response.send_message("Server only.", ephemeral=True); return
    await interaction.response.defer(ephemeral=False) # Make public
    guild_data = load_guild_data(str(interaction.guild.id), interaction.guild.name)
    user_data = get_user_data_block(str(interaction.guild.id), str(target_user.id), guild_data)
    unlocked_keys = user_data.get("unlocked_achievements", [])
    embed = discord.Embed(title=f"🏆 {target_user.display_name}'s Achievements ({len(unlocked_keys)}/{len(ACHIEVEMENTS)})", color=discord.Color.gold())
    if target_user.avatar: embed.set_thumbnail(url=target_user.avatar.url)
    
    description_lines = []
    sorted_ach_keys = sorted(ACHIEVEMENT_KEYS) # Sort all achievement keys for consistent display order

    for ach_key in sorted_ach_keys:
        ach_info = ACHIEVEMENTS[ach_key]
        if ach_key in unlocked_keys:
            description_lines.append(f"{ach_info.get('emoji', '✅')} **{ach_info['name']}**: _{ach_info['description']}_")
        else:
            description_lines.append(f"🔒 **{ach_info['name']}**: _{ach_info['description']}_")
            
    if not description_lines: embed.description = "No achievements defined or found."
    else: embed.description = "\n\n".join(description_lines)
    
    await interaction.followup.send(embed=embed)

# --- LEADERBOARD COMMAND ---
@bot.tree.command(name="leaderboard", description="Shows server leaderboards for dogs.")
@app_commands.describe(category="The leaderboard category to display.")
@app_commands.choices(category=[
    app_commands.Choice(name="Richest (Total Dog Value)", value="value"),
    app_commands.Choice(name="Most Dogs (Total Count)", value="count")
])
async def leaderboard_slash(interaction: discord.Interaction, category: str = "value"):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=False)
    guild_data = load_guild_data(str(interaction.guild.id), interaction.guild.name)
    user_overall_data = guild_data.get("user_data", {})
    if not user_overall_data:
        await interaction.followup.send("No user data found for this server to generate a leaderboard.")
        return
    leaderboard_entries = []
    for user_id_str, user_data_block in user_overall_data.items():
        user_dog_inventory = user_data_block.get("inventory", {})
        if not isinstance(user_dog_inventory, dict): continue
        total_value = 0; total_dogs = 0
        for dog_key, count in user_dog_inventory.items():
            if dog_key in DOG_TYPES and count > 0:
                total_value += DOG_TYPES[dog_key].get("value", 0) * count
                total_dogs += count
        if total_dogs > 0 or total_value > 0:
            user_display_name_or_mention = f"User ID: {user_id_str}"
            try:
                member = interaction.guild.get_member(int(user_id_str))
                if member: user_display_name_or_mention = member.mention
            except ValueError: pass # Should not happen with Discord IDs
            leaderboard_entries.append({"name_mention": user_display_name_or_mention, "total_value": total_value, "total_dogs": total_dogs})
    if not leaderboard_entries:
        await interaction.followup.send("No users with dogs/value found to create a leaderboard.")
        return
    if category == "value":
        sorted_leaderboard = sorted(leaderboard_entries, key=lambda x: x["total_value"], reverse=True)
        title = "💎 Richest Collectors (Total Dog Value)"; entry_format = lambda i, e: f"**{i+1}.** {e['name_mention']} - Value: {e['total_value']} ✨"
    else: # category == "count"
        sorted_leaderboard = sorted(leaderboard_entries, key=lambda x: x["total_dogs"], reverse=True)
        title = "🏆 Top Dog Owners (Total Count)"; entry_format = lambda i, e: f"**{i+1}.** {e['name_mention']} - Dogs: {e['total_dogs']}"
    embed = discord.Embed(title=title, color=discord.Color.gold())
    description_lines = [entry_format(i, entry) for i, entry in enumerate(sorted_leaderboard[:15])]
    if description_lines: embed.description = "\n".join(description_lines)
    else: embed.description = "No one qualifies for this leaderboard yet!"
    await interaction.followup.send(embed=embed)
@leaderboard_slash.error
async def leaderboard_slash_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f"Error in /leaderboard: {error}");
    if hasattr(error, 'original'): import traceback; traceback.print_exception(type(error.original), error.original, error.original.__traceback__)
    if not interaction.response.is_done(): await interaction.response.send_message("Error fetching leaderboard.", ephemeral=True)
    else: await interaction.followup.send("Error fetching leaderboard.", ephemeral=True)

# --- CATALOGUE COMMAND ---
@bot.tree.command(name="catalogue", description="Displays a catalogue of all dog types, their rarity, and server counts.")
async def catalogue_slash(interaction: discord.Interaction):
    if not interaction.guild: await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    await interaction.response.defer(ephemeral=False)
    guild_id_str = str(interaction.guild.id); guild_data = load_guild_data(guild_id_str, interaction.guild.name)
    server_dog_counts = {dog_key: 0 for dog_key in DOG_TYPE_KEYS}
    if "user_data" in guild_data and isinstance(guild_data["user_data"], dict):
        for user_id, user_specific_data in guild_data["user_data"].items():
            user_inventory = user_specific_data.get("inventory", {})
            if isinstance(user_inventory, dict):
                for dog_key, count in user_inventory.items():
                    if dog_key in server_dog_counts: server_dog_counts[dog_key] += count
    total_spawn_weight = sum(DOG_SPAWN_WEIGHTS_FOR_RANDOM); 
    if total_spawn_weight == 0: total_spawn_weight = 1
    embed = discord.Embed(title=f"🐾 Dog Catalogue for {interaction.guild.name}", description="Dog types, spawn chance, and server population.", color=discord.Color.purple())
    display_dogs_info = []
    for key in DOG_TYPE_KEYS:
        props = DOG_TYPES.get(key, {}); spawn_weight = props.get("spawn_weight", 0); rarity_percent = 0.0
        if key in DOG_SPAWN_KEYS_FOR_RANDOM and total_spawn_weight > 0: rarity_percent = (spawn_weight / total_spawn_weight) * 100
        display_dogs_info.append({ "key": key, "name": props.get("display_name", key.replace("_", " ").title()), "emoji_name": props.get("emoji_name"), "emoji_id": props.get("emoji_id"), "server_count": server_dog_counts.get(key, 0), "rarity_percent": rarity_percent, "value": props.get("value", 0)})
    sorted_display_dogs = sorted(display_dogs_info, key=lambda x: x["value"], reverse=False)
    description_lines = []
    for dog_info in sorted_display_dogs:
        emoji_str = f"<:{dog_info['emoji_name']}:{dog_info['emoji_id']}> " if dog_info["emoji_name"] and dog_info["emoji_id"] else "❓ "
        rarity_display = f"{dog_info['rarity_percent']:.4f}%"
        if dog_info['rarity_percent'] == 0 and dog_info['key'] not in DOG_SPAWN_KEYS_FOR_RANDOM : rarity_display = "N/A (Non-Spawn)"
        description_lines.append(f"{emoji_str}**{dog_info['name']}**\n   - In Server: {dog_info['server_count']}\n   - Spawn Chance: {rarity_display}")
    if description_lines:
        full_description = "\n\n".join(description_lines)
        if len(full_description) > 4096: embed.description = full_description[:4000] + "\n... (list truncated)"
        else: embed.description = full_description
    else: embed.description = "No dog types found."
    await interaction.followup.send(embed=embed)
@catalogue_slash.error
async def catalogue_slash_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f"Error in /catalogue: {error}"); import traceback
    if hasattr(error, 'original'): traceback.print_exception(type(error.original), error.original, error.original.__traceback__)
    else: traceback.print_exception(type(error), error, error.__traceback__)
    if not interaction.response.is_done(): await interaction.response.send_message("Error fetching catalogue.", ephemeral=True)
    else: await interaction.followup.send("Error fetching catalogue.", ephemeral=True)

# --- SETUP COMMANDS ---
setup_group = app_commands.Group(name="setup", description="Configure bot settings for this server.")
@setup_group.command(name="spawnchannel", description="Manage channels where dogs can spawn.")
@app_commands.describe(action="'add' or 'remove' a channel, or 'clear' all. 'list' to view.", channel="The channel to add or remove (not needed for 'clear' or 'list').")
@app_commands.choices(action=[app_commands.Choice(name="Add spawn channel", value="add"), app_commands.Choice(name="Remove spawn channel", value="remove"), app_commands.Choice(name="List spawn channels", value="list"), app_commands.Choice(name="Clear all (dogs won't spawn until one is added!)", value="clear")])
@app_commands.checks.has_permissions(administrator=True)
async def setup_spawnchannel_slash(interaction: discord.Interaction, action: str, channel: discord.TextChannel = None):
    if not interaction.guild: await interaction.response.send_message("Server only.",ephemeral=True); return
    gid = str(interaction.guild.id); guild_data = load_guild_data(gid, interaction.guild.name)
    settings = guild_data.setdefault("settings", {}); spawn_channels = settings.setdefault("spawn_channel_ids", [])
    action_message = ""
    if action == "add":
        if not channel: await interaction.response.send_message("Please specify a channel to add.",ephemeral=True); return
        if channel.id not in spawn_channels: spawn_channels.append(channel.id); action_message = f"✅ {channel.mention} added. Dogs can now spawn here."
        else: action_message = f"ℹ️ {channel.mention} is already a spawn location."
    elif action == "remove":
        if not channel: await interaction.response.send_message("Please specify a channel to remove.",ephemeral=True); return
        if channel.id in spawn_channels:
            spawn_channels.remove(channel.id); action_message = f"➖ {channel.mention} removed."
            if not spawn_channels: action_message += " No specific channels set; dogs will NOT spawn until one is added."
        else: action_message = f"ℹ️ {channel.mention} was not in the list."
    elif action == "clear":
        if not spawn_channels: await interaction.response.send_message("ℹ️ No specific spawn channels were set. Dogs will NOT spawn until one is added.",ephemeral=True); return
        spawn_channels.clear(); action_message = "✅ Spawn locations cleared. Dogs will NOT spawn until channels are added using `/setup spawnchannel add`."
    elif action == "list":
        if not spawn_channels: await interaction.response.send_message("No specific spawn channels set. Dogs will NOT spawn until one is added via `/setup spawnchannel add`.",ephemeral=True); return
        channel_mentions = [f"<#{ch_id}>" for ch_id in spawn_channels if interaction.guild.get_channel(ch_id)]
        await interaction.response.send_message(f"ℹ️ Current spawn channels: {', '.join(channel_mentions) if channel_mentions else 'None (or channels no longer exist)'}.",ephemeral=True); return
    else: await interaction.response.send_message("Invalid action.",ephemeral=True); return
    settings["spawn_channel_ids"] = spawn_channels
    if save_guild_data(gid, guild_data, interaction.guild.name): await interaction.response.send_message(action_message)
    else: await interaction.response.send_message("❌ Error saving settings.", ephemeral=True)
@setup_spawnchannel_slash.error
async def setup_spawnchannel_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions): await interaction.response.send_message("⛔ Admins only.", ephemeral=True)
    else: await interaction.response.send_message(f"🤔 Err: {type(error).__name__}", ephemeral=True); print(f"Err /setup spawnchannel: {error}")
bot.tree.add_command(setup_group) # Add the setup group to the tree

# --- CRAFTING SYSTEM COMMANDS ---
@bot.tree.command(name="togglecrafting", description="Admin: Enable or disable the crafting system for this server.")
@app_commands.describe(enabled="True to enable, False to disable")
@app_commands.checks.has_permissions(administrator=True)
async def togglecrafting_slash(interaction: discord.Interaction, enabled: bool):
    if not interaction.guild: await interaction.response.send_message("Server only.", ephemeral=True); return
    gd = load_guild_data(str(interaction.guild.id), interaction.guild.name);gd.setdefault("settings", {})["crafting_enabled"] = enabled
    if save_guild_data(str(interaction.guild.id), gd, interaction.guild.name): await interaction.response.send_message(f"✅ Crafting system {('enabled' if enabled else 'disabled')}.")
    else: await interaction.response.send_message("❌ Error updating crafting status.", ephemeral=True)

@bot.tree.command(name="adddogrecipe", description="Admin: Add/update a dog crafting recipe (max 3 ingredients).")
@app_commands.describe( recipe_key="Unique key (e.g., void_dog_craft).", output_dog_key="The dog this recipe produces.", display_name="Display name for /craftables.", ing1_type="Type of  1st ingredient.", ing1_amount="Amount of 1st.", ing2_type="2nd ingredient type (opt).", ing2_amount="Amount of 2nd (opt).", ing3_type="3rd ingredient type (opt).", ing3_amount="Amount of 3rd (opt).", emoji_name="Output dog emoji name (opt).", emoji_id="Output dog emoji ID (opt).")
@app_commands.choices( output_dog_key=[app_commands.Choice(name=props["display_name"], value=key) for key, props in DOG_TYPES.items()], ing1_type=[app_commands.Choice(name=props["display_name"], value=key) for key, props in DOG_TYPES.items()], ing2_type=[app_commands.Choice(name=props["display_name"], value=key) for key, props in DOG_TYPES.items()], ing3_type=[app_commands.Choice(name=props["display_name"], value=key) for key, props in DOG_TYPES.items()])
@app_commands.checks.has_permissions(administrator=True)
async def add_dog_recipe_slash(interaction: discord.Interaction, recipe_key: str, output_dog_key: str, display_name: str, ing1_type: str, ing1_amount: app_commands.Range[int, 1, None], ing2_type: str = None, ing2_amount: app_commands.Range[int, 1, None] = None, ing3_type: str = None, ing3_amount: app_commands.Range[int, 1, None] = None, emoji_name: str = None, emoji_id: str = None):
    if not interaction.guild: await interaction.response.send_message("Srv only.", ephemeral=True); return
    ingredients = {};
    if ing1_type and ing1_amount:
        if ing1_type not in DOG_TYPES: await interaction.response.send_message(f"Inv ing1 type: {ing1_type}", ephemeral=True); return
        ingredients[ing1_type] = ing1_amount
    if ing2_type and ing2_amount:
        if ing2_type not in DOG_TYPES: await interaction.response.send_message(f"Inv ing2 type: {ing2_type}", ephemeral=True); return
        ingredients[ing2_type] = ing2_amount
    elif (ing2_type and not ing2_amount) or (not ing2_type and ing2_amount): await interaction.response.send_message("Ing2 type/amount mismatch.", ephemeral=True); return
    if ing3_type and ing3_amount:
        if ing3_type not in DOG_TYPES: await interaction.response.send_message(f"Inv ing3 type: {ing3_type}", ephemeral=True); return
        ingredients[ing3_type] = ing3_amount
    elif (ing3_type and not ing3_amount) or (not ing3_type and ing3_amount): await interaction.response.send_message("Ing3 type/amount mismatch.", ephemeral=True); return
    if not ingredients: await interaction.response.send_message("At least one ingredient needed.", ephemeral=True); return
    if output_dog_key not in DOG_TYPES: await interaction.response.send_message(f"Output dog key '{output_dog_key}' invalid.", ephemeral=True); return
    gd = load_guild_data(str(interaction.guild.id), interaction.guild.name); recipes_data = gd.setdefault("crafting_recipes", {}).setdefault("dogs", {})
    clean_recipe_key = recipe_key.lower().replace(" ", "_").strip()
    if not clean_recipe_key: await interaction.response.send_message("Recipe key empty.", ephemeral=True); return
    if output_dog_key in DOG_TYPES and emoji_name and emoji_id: DOG_TYPES[output_dog_key]["emoji_name"] = emoji_name; DOG_TYPES[output_dog_key]["emoji_id"] = emoji_id
    recipes_data[clean_recipe_key] = {"display_name": display_name, "output_dog_key": output_dog_key, "enabled": True, "ingredients": ingredients, "recipe_emoji_name": emoji_name if emoji_name else DOG_TYPES[output_dog_key].get("emoji_name"), "recipe_emoji_id": emoji_id if emoji_id else DOG_TYPES[output_dog_key].get("emoji_id")}
    if save_guild_data(str(interaction.guild.id), gd, interaction.guild.name): await interaction.response.send_message(f"✅ Dog recipe '{clean_recipe_key}' for **{DOG_TYPES[output_dog_key]['display_name']}** saved.")
    else: await interaction.response.send_message("❌ Err saving recipe.", ephemeral=True)

@bot.tree.command(name="addreactorrecipe", description="Admin: Add/update an Arc Reactor recipe (max 3 dog ingredients).")
@app_commands.describe(
    recipe_key="Unique key (e.g., theft_booster).", 
    output_reactor_key="The Arc Reactor this recipe produces.", 
    display_name="Display name in /craftables.", 
    ingredients="Dog ingredients as 'key:amount,key2:amount'. Max 3.", 
    recipe_emoji="Emoji for this recipe in /craftables (optional, e.g., 💥)." # Changed from emoji_name/id
)
@app_commands.choices( # ONLY for output_reactor_key
    output_reactor_key=[app_commands.Choice(name=props["display_name"], value=key) for key, props in ARC_REACTOR_TYPES.items()]
)
@app_commands.checks.has_permissions(administrator=True)
async def add_reactor_recipe_slash(
    interaction: discord.Interaction, 
    recipe_key: str, 
    output_reactor_key: str, 
    display_name: str, 
    ingredients: str, # Ingredients are parsed from this string
    recipe_emoji: str = None # Changed from emoji_name/id to a single emoji string
):
    if not interaction.guild: await interaction.response.send_message("Server only.", ephemeral=True); return
    parsed_ingredients = parse_ingredients(ingredients) # parse_ingredients should only expect dog keys
    if parsed_ingredients is None: 
        await interaction.response.send_message("Invalid ingredients. Use valid dog keys: 'key1:amt1,key2:amt2'.", ephemeral=True); return
    if output_reactor_key not in ARC_REACTOR_TYPES: 
        await interaction.response.send_message(f"Output reactor key '{output_reactor_key}' invalid.", ephemeral=True); return
    
    gd = load_guild_data(str(interaction.guild.id), interaction.guild.name)
    recipes = gd.setdefault("crafting_recipes", {}).setdefault("arc_reactors", {})
    clean_recipe_key = recipe_key.lower().replace(" ", "_").strip()
    if not clean_recipe_key: 
        await interaction.response.send_message("Recipe key cannot be empty.", ephemeral=True); return

    recipes[clean_recipe_key] = {
        "display_name": display_name, 
        "output_reactor_key": output_reactor_key, 
        "enabled": True, 
        "ingredients": parsed_ingredients, # Use parsed ingredients
        "recipe_display_emoji": recipe_emoji if recipe_emoji else ARC_REACTOR_TYPES[output_reactor_key].get("emoji", "⚙️") # Direct emoji or reactor's default
    }
    if save_guild_data(str(interaction.guild.id), gd, interaction.guild.name): await interaction.response.send_message(f"✅ Arc Reactor recipe '{clean_recipe_key}' for **{ARC_REACTOR_TYPES[output_reactor_key]['display_name']}** saved.")
    else: await interaction.response.send_message("❌ Err saving recipe.", ephemeral=True)

def parse_ingredients(ingredients_str: str) -> dict | None:
    ingredients = {}
    if not ingredients_str or not ingredients_str.strip(): # Handle empty or whitespace-only string
        logger.warning("Parse Ingredient Error: Empty ingredients string provided.")
        return None # Or return {} if an empty ingredient list is acceptable for some recipes

    parts = ingredients_str.split(',')
    if not parts:
        logger.warning(f"Parse Ingredient Error: No parts found after splitting '{ingredients_str}'")
        return None

    for part in parts:
        item = part.strip().split(':')
        if len(item) != 2: 
            logger.warning(f"Parse Ingredient Error: Invalid format part '{part}' in '{ingredients_str}'")
            return None 
        
        raw_dog_key, amount_str = item[0].strip(), item[1].strip()
        
        # Try to match by key first, then by display name (case-insensitive)
        found_key = None
        # Exact key match (case sensitive, as dict keys are)
        if raw_dog_key in DOG_TYPES:
            found_key = raw_dog_key
        else: # Try case-insensitive display name match
            for dt_key, dt_props in DOG_TYPES.items():
                if dt_props['display_name'].lower() == raw_dog_key.lower():
                    found_key = dt_key
                    break
                    for dt_key in DOG_TYPES.keys():
                        if dt_key.lower() == raw_dog_key.lower():
                            found_key = dt_key
                            break

        if not found_key: 
            logger.warning(f"Parse Ingredient Error: Invalid dog type '{raw_dog_key}' in '{ingredients_str}' - not found in DOG_TYPES by key or display name.")
            return None 
        try: 
            amount = int(amount_str)
            if amount <= 0: 
                logger.warning(f"Parse Ingredient Error: Amount not positive for '{raw_dog_key}' in '{ingredients_str}'")
                return None
            ingredients[found_key] = amount # Store with the correct, canonical DOG_TYPES key
        except ValueError: 
            logger.warning(f"Parse Ingredient Error: Amount not integer for '{raw_dog_key}' in '{ingredients_str}'")
            return None
            
    return ingredients if ingredients else None

@bot.tree.command(name="craftables", description="View available crafting recipes.")
@app_commands.describe(category="Which category of craftables to view.")
@app_commands.choices(category=[app_commands.Choice(name="All Dogs", value="dogs"), app_commands.Choice(name="All Arc Reactors", value="arc_reactors"), app_commands.Choice(name="All Items", value="all")])
async def craftables_slash(interaction: discord.Interaction, category: str = "all"):
    if not interaction.guild: await interaction.response.send_message("Server only.",ephemeral=True); return
    gd = load_guild_data(str(interaction.guild.id), interaction.guild.name)
    if not gd.get("settings", {}).get("crafting_enabled", False): await interaction.response.send_message("🛠️ Crafting disabled.", ephemeral=True); return
    all_recipes = gd.get("crafting_recipes", {}); emb = discord.Embed(title="Crafting Recipes", color=discord.Color.gold()); found = False
    cats_to_show = ["dogs", "arc_reactors"] if category == "all" else ([category] if category in ["dogs", "arc_reactors"] else [])
    for cat_key in cats_to_show:
        cat_name = "Dog Recipes" if cat_key == "dogs" else ("Arc Reactor Recipes" if cat_key == "arc_reactors" else "Other Recipes")
        recipes_in_cat = all_recipes.get(cat_key, {}); cat_txt = []
        for rk, rd in recipes_in_cat.items():
            if rd.get("enabled", False):
                output_dn = rd.get("display_name", rk.replace("_", " ").title()); final_emoji_str = "❓ "
                if cat_key == "dogs":
                    odk = rd.get("output_dog_key")
                    if odk and odk in DOG_TYPES: output_dn = DOG_TYPES[odk]["display_name"]
                    ren, rei = rd.get("recipe_emoji_name"), rd.get("recipe_emoji_id"); den, dei = DOG_TYPES.get(odk,{}).get("emoji_name"), DOG_TYPES.get(odk,{}).get("emoji_id")
                    en_use, ei_use = (ren if ren else den), (rei if rei else dei)
                    if en_use and ei_use: final_emoji_str = f"<:{en_use}:{ei_use}> "
                    else: final_emoji_str = "❓ "
                elif cat_key == "arc_reactors":
                    ork = rd.get("output_reactor_key")
                    if ork and ork in ARC_REACTOR_TYPES: output_dn = ARC_REACTOR_TYPES[ork]["display_name"]
                    recipe_display_emo = rd.get("recipe_display_emoji")
                    if recipe_display_emo: final_emoji_str = recipe_display_emo + " "
                    elif ork and ork in ARC_REACTOR_TYPES: final_emoji_str = ARC_REACTOR_TYPES[ork].get("emoji", "⚙️") + " "
                    else: final_emoji_str = "⚙️ "
                ings = ", ".join([f"{DOG_TYPES.get(ik,{}).get('display_name',ik)} x{amt}" for ik,amt in rd.get("ingredients",{}).items()]) or "None"
                cat_txt.append(f"**{final_emoji_str}{output_dn}** (`/craft {rk}`)\nIngredients: _{ings}_")
        if cat_txt: emb.add_field(name=f"--- {cat_name} ---", value="\n\n".join(cat_txt), inline=False); found = True
    if not found: emb.description = "No craftables available/enabled."
    await interaction.response.send_message(embed=emb, ephemeral=True)

@bot.tree.command(name="craft", description="Craft an item from a recipe.")
@app_commands.describe(recipe_key="The unique key of the recipe to craft (see /craftables).")
async def craft_slash(interaction: discord.Interaction, recipe_key: str):
    if not interaction.guild: 
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    gid = str(interaction.guild.id)
    uid_s = str(interaction.user.id)
    guild_data = load_guild_data(gid, interaction.guild.name) # Load guild_data once

    if not guild_data.get("settings", {}).get("crafting_enabled", False):
        await interaction.response.send_message("🛠️ Crafting is currently disabled on this server.", ephemeral=True)
        return

    rclean = recipe_key.lower().replace(" ", "_")
    recipe_data = None
    recipe_category = None

    for cat, recipes_in_cat in guild_data.get("crafting_recipes", {}).items():
        if rclean in recipes_in_cat:
            if recipes_in_cat[rclean].get("enabled", False):
                recipe_data = recipes_in_cat[rclean]
                recipe_category = cat
                break
            else:
                await interaction.response.send_message(f"Recipe '{recipe_key}' is currently disabled.", ephemeral=True)
                return
    
    if not recipe_data:
        await interaction.response.send_message(f"Recipe '{recipe_key}' not found or is not enabled. Use `/craftables` to see available recipes.", ephemeral=True)
        return

    user_data = get_user_data_block(gid, uid_s, guild_data) # Pass loaded guild_data
    user_dog_inventory = user_data["inventory"] 
    user_arc_reactors = user_data.setdefault("arc_reactors", {k:0 for k in ARC_REACTOR_TYPE_KEYS})

    can_craft = True
    missing_ingredients = []
    for ing_key, required_amount in recipe_data.get("ingredients", {}).items():
        if ing_key in DOG_TYPES: # Assuming ingredients are only dogs for now
            current_amount = user_dog_inventory.get(ing_key, 0)
            if current_amount < required_amount:
                can_craft = False
                missing_ingredients.append(f"{DOG_TYPES[ing_key]['display_name']} (Need: {required_amount}, Have: {current_amount})")
        # Extend here if recipes can use arc_reactors as ingredients
        # elif ing_key in ARC_REACTOR_TYPES: ...
        else:
            can_craft = False
            missing_ingredients.append(f"Unknown ingredient type: {ing_key}")
            
    if not can_craft:
        await interaction.response.send_message(f"You can't craft **{recipe_data['display_name']}** yet. Missing:\n- " + "\n- ".join(missing_ingredients), ephemeral=True)
        return

    # Deduct ingredients
    for ing_key, required_amount in recipe_data.get("ingredients", {}).items():
        if ing_key in DOG_TYPES:
             user_dog_inventory[ing_key] -= required_amount
        # Deduct other types if they become ingredients

    # Add crafted item
    output_display_name = recipe_data['display_name']
    output_emoji_str = ""
    crafted_item_key_for_quest = "" # To pass to quest update

    if recipe_category == "dogs":
        output_dog_key = recipe_data["output_dog_key"]
        user_dog_inventory[output_dog_key] = user_dog_inventory.get(output_dog_key, 0) + 1
        crafted_item_key_for_quest = output_dog_key
        if output_dog_key in DOG_TYPES: 
            dog_info = DOG_TYPES[output_dog_key]
            output_display_name = dog_info["display_name"]
            # Use recipe-specific emoji first, then dog's default from DOG_TYPES
            e_name = recipe_data.get("recipe_emoji_name", dog_info.get("emoji_name"))
            e_id = recipe_data.get("recipe_emoji_id", dog_info.get("emoji_id"))
            if e_name and e_id: output_emoji_str = f"<:{e_name}:{e_id}> "
            else: output_emoji_str = "❓ "
    elif recipe_category == "arc_reactors":
        output_reactor_key = recipe_data["output_reactor_key"]
        user_arc_reactors[output_reactor_key] = user_arc_reactors.get(output_reactor_key, 0) + 1
        crafted_item_key_for_quest = output_reactor_key
        if output_reactor_key in ARC_REACTOR_TYPES:
            reactor_info = ARC_REACTOR_TYPES[output_reactor_key]
            output_display_name = reactor_info["display_name"]
            # Use recipe-specific display emoji, then reactor's default from ARC_REACTOR_TYPES
            recipe_emo = recipe_data.get("recipe_display_emoji") # This is a direct emoji string
            if recipe_emo: output_emoji_str = recipe_emo + " "
            else: output_emoji_str = reactor_info.get("emoji", "⚙️") + " "
        else: # Fallback if output_reactor_key somehow not in ARC_REACTOR_TYPES
            output_emoji_str = recipe_data.get("recipe_display_emoji", "⚙️") + " "
    
    save_guild_data(gid, guild_data, interaction.guild.name) # Save changes to inventory/reactors

    # Call quest and achievement updates
    await update_quest_progress(interaction, uid_s, gid, "craft", {"item_key": crafted_item_key_for_quest, "category": recipe_category})
    # check_achievements_and_chest is now called at the end of update_quest_progress

    await interaction.response.send_message(f"🎉 Successfully crafted {output_emoji_str}**{output_display_name}**!")

@bot.tree.command(name="usearc", description="Activate an Arc Reactor from your inventory.")
@app_commands.describe(reactor_key="The Arc Reactor you want to use.")
@app_commands.choices(reactor_key=[app_commands.Choice(name=props["display_name"], value=key) for key, props in ARC_REACTOR_TYPES.items()])
async def use_arc_reactor_slash(interaction: discord.Interaction, reactor_key: str):
    if not interaction.guild: await interaction.response.send_message("Server only.", ephemeral=True); return
    gid = str(interaction.guild.id); uid = str(interaction.user.id); guild_data = load_guild_data(gid, interaction.guild.name)
    user_data = get_user_data_block(guild_id=gid, uid=uid, guild_data_ref=guild_data); user_reactors = user_data.setdefault("arc_reactors", {k:0 for k in ARC_REACTOR_TYPE_KEYS})
    if reactor_key not in ARC_REACTOR_TYPES: await interaction.response.send_message("Invalid Arc Reactor type.", ephemeral=True); return
    if user_reactors.get(reactor_key, 0) <= 0: await interaction.response.send_message(f"You don't have any **{ARC_REACTOR_TYPES[reactor_key]['display_name']}**.", ephemeral=True); return
    reactor_info = ARC_REACTOR_TYPES[reactor_key]; effect_type = reactor_info.get("effect_type"); duration = reactor_info.get("duration_seconds", 0); current_time = int(datetime.now(timezone.utc).timestamp()); active_effects = user_data.setdefault("active_effects", {})
    user_reactors[reactor_key] -= 1; activation_message = f"{reactor_info.get('emoji','💥')} Activated **{reactor_info['display_name']}**!"
    if effect_type == "double_catch": expiry_time = current_time + duration; active_effects["double_catch_until"] = expiry_time; activation_message += f" Double catches for {format_time_delta(duration)} (until {discord.utils.format_dt(datetime.fromtimestamp(expiry_time, timezone.utc), style='R')})."
    elif effect_type == "theft_boost": expiry_time = current_time + duration; active_effects["theft_boost_until"] = expiry_time; active_effects["theft_boost_value"] = 0.15; activation_message += f" Theft chance boosted by 15% for {format_time_delta(duration)} (until {discord.utils.format_dt(datetime.fromtimestamp(expiry_time, timezone.utc), style='R')})."
    elif effect_type == "shield_bypass_on_steal": active_effects["next_steal_bypass_attempt"] = True; activation_message = f"🛡️💨 **{reactor_info['display_name']}** charged! Next `/steal` attempts shield bypass."
    else: activation_message = f"Hmm, **{reactor_info['display_name']}** used, effect TBD."
    if save_guild_data(gid, guild_data, interaction.guild.name): await interaction.response.send_message(activation_message)
    else: user_reactors[reactor_key] += 1; await interaction.response.send_message("❌ Error activating Arc Reactor.", ephemeral=True)

# --- SHIELD COMMANDS ---
shield_group = app_commands.Group(name="shield", description="Manage your dog protection shield.")
@shield_group.command(name="buy", description=f"Buy a shield for {SHIELD_DURATION_HOURS} hours (Costs: {SHIELD_COST_NORMAL_DOGS} Normal Dogs).")
async def shield_buy_slash(interaction: discord.Interaction):
    if not interaction.guild: await interaction.response.send_message("Server only.",ephemeral=True); return
    gid = str(interaction.guild.id); uid = str(interaction.user.id); guild_data = load_guild_data(gid, interaction.guild.name); user_data = get_user_data_block(gid, uid, guild_data)
    user_inventory = user_data["inventory"]; current_time = int(datetime.now(timezone.utc).timestamp())
    if user_data.get("shield_active_until", 0) > current_time: await interaction.response.send_message(f"🛡️ Already active! Expires in {format_time_delta(user_data['shield_active_until'] - current_time)}.", ephemeral=True); return
    if user_inventory.get("normal_dog", 0) < SHIELD_COST_NORMAL_DOGS: await interaction.response.send_message(f"Need {SHIELD_COST_NORMAL_DOGS} Normal Dogs (Have {user_inventory.get('normal_dog',0)}).", ephemeral=True); return
    user_inventory["normal_dog"] -= SHIELD_COST_NORMAL_DOGS; user_data["shield_active_until"] = current_time + (SHIELD_DURATION_HOURS * 3600)
    if save_guild_data(gid, guild_data, interaction.guild.name): await interaction.response.send_message(f"🛡️ Shield purchased for {SHIELD_DURATION_HOURS} hours (until {discord.utils.format_dt(datetime.fromtimestamp(user_data['shield_active_until'], timezone.utc), style='R')}).")
    else: user_inventory["normal_dog"] += SHIELD_COST_NORMAL_DOGS; await interaction.response.send_message("❌ Error buying shield.", ephemeral=True)
@shield_group.command(name="status", description="Check your current shield status.")
async def shield_status_slash(interaction: discord.Interaction):
    if not interaction.guild: await interaction.response.send_message("Server only.",ephemeral=True); return
    gid = str(interaction.guild.id); uid = str(interaction.user.id); guild_data = load_guild_data(gid, interaction.guild.name); user_data = get_user_data_block(gid, uid, guild_data) 
    shield_until = user_data.get("shield_active_until", 0); current_time = int(datetime.now(timezone.utc).timestamp())
    if shield_until > current_time: await interaction.response.send_message(f"🛡️ Shield **ACTIVE**, expires in {format_time_delta(shield_until - current_time)} ({discord.utils.format_dt(datetime.fromtimestamp(shield_until, timezone.utc), style='R')}).", ephemeral=True)
    else: await interaction.response.send_message("🛡️ Shield **INACTIVE**.", ephemeral=True)
bot.tree.add_command(shield_group)

# --- STEAL COMMAND ---
@bot.tree.command(name="steal", description="Attempt to steal a dog from another user.")
@app_commands.describe(target="The user you want to attempt to steal from.")
async def steal_slash(interaction: discord.Interaction, target: discord.Member):
    if not interaction.guild: await interaction.response.send_message("Server only.",ephemeral=True); return
    if target == interaction.user: await interaction.response.send_message("Can't steal from yourself!", ephemeral=True); return
    if target.bot: await interaction.response.send_message("Can't steal from bots!", ephemeral=True); return
    gid = str(interaction.guild.id); thief_id = str(interaction.user.id); victim_id = str(target.id); current_time = int(datetime.now(timezone.utc).timestamp())
    guild_data = load_guild_data(gid, interaction.guild.name); thief_data = get_user_data_block(gid, thief_id, guild_data); victim_data = get_user_data_block(gid, victim_id, guild_data)
    if thief_data.get("spawn_catch_banned_until", 0) > current_time: await interaction.response.send_message(f"🚓 Banned until {discord.utils.format_dt(datetime.fromtimestamp(thief_data['spawn_catch_banned_until'], timezone.utc), style='R')}.",ephemeral=True); return
    victim_shield_active = victim_data.get("shield_active_until", 0) > current_time; shield_bypassed_this_attempt = False
    thief_active_effects = thief_data.setdefault("active_effects", {})
    if victim_shield_active:
        if thief_active_effects.get("next_steal_bypass_attempt", False):
            thief_active_effects["next_steal_bypass_attempt"] = False # Consume charge
            if random.random() < SHIELD_BYPASS_CHANCE_WITH_REACTOR: shield_bypassed_this_attempt = True
        if not shield_bypassed_this_attempt: await interaction.response.send_message(f"🛡️ {target.display_name} shield blocked theft!", ephemeral=True); save_guild_data(gid, guild_data, interaction.guild.name); return
    actual_theft_chance = THEFT_SUCCESS_CHANCE; theft_boost_info = ""
    if thief_active_effects.get("theft_boost_until", 0) > current_time:
        boost_val = thief_active_effects.get("theft_boost")
        if boost_val: actual_theft_chance += boost_val
        theft_boost_info = f" (Boosted by Reactor!)"
    steal_roll = random.random()
    if steal_roll < actual_theft_chance:
        # Successful steal
        stolen_dog_key = random.choices(DOG_SPAWN_KEYS_FOR_RANDOM, weights=DOG_SPAWN_WEIGHTS_FOR_RANDOM, k=1)[0]
        thief_data["inventory"][stolen_dog_key] = thief_data["inventory"].get(stolen_dog_key, 0) + 1
        await interaction.response.send_message(f"🦴 Stole a {DOG_TYPES[stolen_dog_key]['display_name']} from {target.display_name}!{theft_boost_info}")
    else:
        # Failed steal
        thief_data["theft_fail_streak"] = thief_data.get("theft_fail_streak", 0) + 1
        if thief_data["theft_fail_streak"] >= MAX_THEFT_FAIL_STREAK_FOR_WANTED:
            thief_data["wanted_level"] = True
            thief_data["spawn_catch_banned_until"] = current_time + (SPAWN_CATCH_BAN_HOURS_ON_WANTED_FAIL * 3600)
            await interaction.response.send_message(f"🚨 {interaction.user.mention} is now WANTED for theft! Banned from spawning/catching for {SPAWN_CATCH_BAN_HOURS_ON_WANTED_FAIL} hours.")
        else:
            await interaction.response.send_message(f"🔫 Failed to steal from {target.display_name}. Attempted theft #{thief_data['theft_fail_streak']}")
    save_guild_data(gid, guild_data, interaction.guild.name)

# --- ADMIN COMMANDS ---
@bot.tree.command(name="givedog", description="Give a dog to a user.")
@app_commands.describe(user="The user to give the dog to.", dog_type="The type of dog to give.", amount="The amount of dogs to give.")
@app_commands.choices(dog_type=[app_commands.Choice(name=props["display_name"], value=key) for key, props in DOG_TYPES.items()])
@app_commands.checks.has_permissions(administrator=True)
async def givedog_slash(interaction: discord.Interaction, user: discord.Member, dog_type: str, amount: app_commands.Range[int, 1, None] = 1):
    if not interaction.guild: await interaction.response.send_message("Server only.", ephemeral=True); return
    gid = str(interaction.guild.id); uid = str(user.id); amount = int(amount)
    guild_data = load_guild_data(gid, interaction.guild.name); target_data = get_user_data_block(gid, uid, guild_data)
    if dog_type in DOG_TYPES:
        target_data["inventory"][dog_type] = target_data["inventory"].get(dog_type, 0) + amount
        if save_guild_data(gid, guild_data, interaction.guild.name): await interaction.response.send_message(f"✅ Gave {amount}x **{DOG_TYPES[dog_type]['display_name']}** to {user.display_name}.")
        else: await interaction.response.send_message("❌ Error giving dog.", ephemeral=True)
    else: await interaction.response.send_message("Invalid dog type.", ephemeral=True)

@bot.tree.command(name="forcespawn", description="Force spawn a dog in a specific channel.")
@app_commands.describe(channel="The channel to spawn the dog in.", dog_type="The type of dog to spawn.")
@app_commands.choices(dog_type=[app_commands.Choice(name=props["display_name"], value=key) for key, props in DOG_TYPES.items()])
@app_commands.checks.has_permissions(administrator=True)
async def forcespawn_slash(interaction: discord.Interaction, channel: discord.TextChannel, dog_type: str):
    if not interaction.guild: await interaction.response.send_message("Server only.",ephemeral=True); return
    gid = str(interaction.guild.id); current_time = int(datetime.now(timezone.utc).timestamp())
    guild_data = load_guild_data(gid, interaction.guild.name); ss = guild_data["spawn_state"]
    if ss.get("next_eligible_spawn_timestamp", 0) > current_time: await interaction.response.send_message("Spawn on cooldown. Try again later.", ephemeral=True); return
    if dog_type in DOG_TYPES:
        di = DOG_TYPES[dog_type]; ip = DOG_IMAGE_PATH_TEMPLATE.format(image_name=di["image_name"])
        mtxt = f"A wild **{di['display_name']}** has appeared! Type `dog` to catch it!"
        try:
            s_msg = await channel.send(mtxt, file=discord.File(ip) if os.path.exists(ip) else None)
            if not os.path.exists(ip):
                logger.warning(f"IMG MISSING: {ip} for {dog_type}")
            s_time = int(datetime.now(timezone.utc).timestamp())
            active_dog_spawns[channel.id] = {"dog_type_key": dog_type, "guild_id": interaction.guild.id, "message_id": s_msg.id, "spawn_timestamp": s_time}
            ss["next_eligible_spawn_timestamp"] = s_time + random.randint(DEFAULT_MIN_SPAWN_SECONDS, DEFAULT_MAX_SPAWN_SECONDS)
            ss["is_in_post_catch_cooldown"] = False
            save_guild_data(gid, guild_data, interaction.guild.name)
            await interaction.response.send_message(f"✅ Spawned **{di['display_name']}** in {channel.mention}.")
        except Exception as e:
            logger.error(f"Err force spawn in {interaction.guild.name}: {e}")
            await interaction.response.send_message("Error forcing spawn.", ephemeral=True)
    else:
        await interaction.response.send_message("Invalid dog type.", ephemeral=True)

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    import sys
    import asyncio
    try:
        # Start the bot only if this script is run directly
        logger.info("Starting bot via __main__ entry point.")
        # You may need to load the token from your config or environment
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "secret.env"))
        TOKEN = os.getenv("DISCORD_BOT_TOKEN")
        if not TOKEN:
            logger.error("DISCORD_BOT_TOKEN not found in environment or secret.env!")
            sys.exit(1)
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Fatal error in __main__: {e}")
        pass
