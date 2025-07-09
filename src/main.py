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

    # Accept any message containing 'dog' (case-insensitive)
    if "dog" in msg.content.lower():
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
        # --- PING BOT ---
        if event_type == "ping_bot" and quest_def.get("objective_type") == "ping_bot":
            current_progress += 1
            made_progress_this_event = True
        # --- VIEW LEADERBOARD ---
        if event_type == "view_leaderboard" and quest_def.get("objective_type") == "view_leaderboard":
            current_progress += 1
            made_progress_this_event = True
        # --- VIEW INVENTORY ---
        if event_type == "view_inventory" and quest_def.get("objective_type") == "view_inventory":
            current_progress += 1
            made_progress_this_event = True
        # --- STEAL ATTEMPT ---
        if event_type == "steal" and quest_def.get("objective_type") == "steal_attempt":
            current_progress += 1
            made_progress_this_event = True
        # --- COLLECT TOTAL ---
        if event_type == "catch" and quest_def.get("objective_type") == "collect_total":
            user_inventory = user_data.get("inventory", {})
            total_dogs_caught = sum(user_inventory.values())
            if total_dogs_caught != current_progress:
                current_progress = total_dogs_caught
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

# --- QUEST DEFINITIONS (Expanded for Variety) ---
QUEST_DEFINITIONS = {
    # Catching quests
    "catch_normals_basic": {"id": "catch_normals_basic", "title": "Normal Dog Roundup", "description": "Catch 3 Normal Dogs.", "objective_type": "catch_specific", "dog_type_key": "normal_dog", "target_count": 3, "reward_type": "dogs", "reward_item_key": "dog_good", "reward_amount": 1},
    "catch_any_starter": {"id": "catch_any_starter", "title": "First Steps", "description": "Catch any 2 dogs.", "objective_type": "catch_any", "target_count": 2, "reward_type": "dogs", "reward_item_key": "uncommon_dog", "reward_amount": 1},
    "catch_variety": {"id": "catch_variety", "title": "Variety Catcher", "description": "Catch 3 different types of dogs.", "objective_type": "catch_variety", "target_count": 3, "reward_type": "dogs", "reward_item_key": "loyal_dog", "reward_amount": 1},
    "catch_uncommon": {"id": "catch_uncommon", "title": "Uncommon Hunter", "description": "Catch 2 Uncommon Dogs.", "objective_type": "catch_specific", "dog_type_key": "uncommon_dog", "target_count": 2, "reward_type": "dogs", "reward_item_key": "fine_dog", "reward_amount": 1},
    # Value quests
    "value_hunter": {"id": "value_hunter", "title": "Value Hunter", "description": "Catch a dog worth at least 500 value.", "objective_type": "catch_value_gte", "target_value": 500, "reward_type": "dogs", "reward_item_key": "fine_dog", "reward_amount": 2},
    "total_value_1": {"id": "total_value_1", "title": "Small Fortune", "description": "Reach a total dog collection value of 500.", "objective_type": "total_value", "target_value": 500, "reward_type": "dogs", "reward_item_key": "fine_dog", "reward_amount": 1},
    # Crafting quests
    "craft_something_simple": {"id": "craft_something_simple", "title": "Tinkerer", "description": "Craft any 1 item.", "objective_type": "craft_any", "target_count": 1, "reward_type": "arc_reactors", "reward_item_key": "charm_of_thieves_luck", "reward_amount": 1},
    # New: Bot interaction quests
    "ping_bot": {"id": "ping_bot", "title": "Say Hi!", "description": "Ping the dog bot using /ping.", "objective_type": "ping_bot", "target_count": 1, "reward_type": "dogs", "reward_item_key": "dog_good", "reward_amount": 1},
    "view_leaderboard": {"id": "view_leaderboard", "title": "Leaderboard Watcher", "description": "View the leaderboard using /leaderboard.", "objective_type": "view_leaderboard", "target_count": 1, "reward_type": "dogs", "reward_item_key": "dog_good", "reward_amount": 1},
    "view_inventory": {"id": "view_inventory", "title": "Inventory Check", "description": "View your inventory using /inventory.", "objective_type": "view_inventory", "target_count": 1, "reward_type": "dogs", "reward_item_key": "dog_good", "reward_amount": 1},
    # New: Steal quest
    "steal_attempt": {"id": "steal_attempt", "title": "Thief in Training", "description": "Attempt to steal a dog using /steal.", "objective_type": "steal_attempt", "target_count": 1, "reward_type": "arc_reactors", "reward_item_key": "charm_of_thieves_luck", "reward_amount": 1},
    # New: Collect quest
    "collect_dogs": {"id": "collect_dogs", "title": "Dog Collector", "description": "Collect 5 dogs in total.", "objective_type": "collect_total", "target_count": 5, "reward_type": "dogs", "reward_item_key": "uncommon_dog", "reward_amount": 1},
}

# --- Assign Random Quests to User ---
def assign_random_quests_to_user(guild_id: str, user_id: str, guild_data: dict, num_quests: int = 3):
    user_data = get_user_data_block(guild_id, user_id, guild_data)
    active_quests = user_data.setdefault("active_quests", {})
    completed = set(user_data.get("completed_quests_lifetime", []))
    # Only assign if user has no active quests
    if active_quests:
        return False
    # Exclude already completed quests (optional, or allow repeats)
    available_quests = [qid for qid in QUEST_DEFINITIONS if qid not in active_quests]
    if not available_quests:
        return False
    chosen = random.sample(available_quests, min(num_quests, len(available_quests)))
    for qid in chosen:
        active_quests[qid] = {"progress": 0}
    return True

# --- Update quest_reset_task to assign quests after reset ---
@tasks.loop(hours=QUEST_RESET_HOURS)
async def quest_reset_task():
    """Periodically resets quests for all users in all guilds and assigns new ones."""
    now = int(datetime.now(timezone.utc).timestamp())
    for g in bot.guilds:
        gd = load_guild_data(str(g.id), g.name)
        changed = False
        for uid, udata in gd.get("user_data", {}).items():
            last_reset = udata.get("last_quest_reset_timestamp", 0)
            if now - last_reset >= QUEST_RESET_HOURS * 3600:
                udata["active_quests"] = {}
                udata["completed_quests_this_cycle"] = []
                udata["last_quest_reset_timestamp"] = now
                assign_random_quests_to_user(str(g.id), uid, gd, num_quests=3)
                changed = True
            # If user has no active quests (e.g. just joined), assign
            elif not udata.get("active_quests"):
                assign_random_quests_to_user(str(g.id), uid, gd, num_quests=3)
                changed = True
        if changed:
            save_guild_data(str(g.id), gd, g.name)

# --- Add /quest manage admin command group ---
quest_manage_group = app_commands.Group(name="quest", description="Admin quest management commands.")

@quest_manage_group.command(name="reset", description="Reset a user's quests.")
@app_commands.describe(user="User to reset quests for.")
@app_commands.checks.has_permissions(administrator=True)
async def quest_reset_slash(interaction: discord.Interaction, user: discord.Member):
    if not interaction.guild:
        await interaction.response.send_message("Server only.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    guild_data = load_guild_data(gid, interaction.guild.name)
    udata = get_user_data_block(gid, str(user.id), guild_data)
    udata["active_quests"] = {}
    udata["completed_quests_this_cycle"] = []
    udata["last_quest_reset_timestamp"] = int(datetime.now(timezone.utc).timestamp())
    assign_random_quests_to_user(gid, str(user.id), guild_data, num_quests=3)
    save_guild_data(gid, guild_data, interaction.guild.name)
    await interaction.response.send_message(f"✅ Reset and assigned new quests for {user.mention}.", ephemeral=True)

@quest_manage_group.command(name="assign", description="Assign a specific quest to a user.")
@app_commands.describe(user="User to assign quest to.", quest_id="Quest ID to assign.")
@app_commands.checks.has_permissions(administrator=True)
async def quest_assign_slash(interaction: discord.Interaction, user: discord.Member, quest_id: str):
    if not interaction.guild:
        await interaction.response.send_message("Server only.", ephemeral=True)
        return
    if quest_id not in QUEST_DEFINITIONS:
        await interaction.response.send_message(f"Invalid quest ID. Valid: {', '.join(QUEST_DEFINITIONS.keys())}", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    guild_data = load_guild_data(gid, interaction.guild.name)
    udata = get_user_data_block(gid, str(user.id), guild_data)
    udata.setdefault("active_quests", {})[quest_id] = {"progress": 0}
    save_guild_data(gid, guild_data, interaction.guild.name)
    await interaction.response.send_message(f"✅ Assigned quest `{quest_id}` to {user.mention}.", ephemeral=True)

@quest_manage_group.command(name="remove", description="Remove a specific quest from a user.")
@app_commands.describe(user="User to remove quest from.", quest_id="Quest ID to remove.")
@app_commands.checks.has_permissions(administrator=True)
async def quest_remove_slash(interaction: discord.Interaction, user: discord.Member, quest_id: str):
    if not interaction.guild:
        await interaction.response.send_message("Server only.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    guild_data = load_guild_data(gid, interaction.guild.name)
    udata = get_user_data_block(gid, str(user.id), guild_data)
    if quest_id in udata.get("active_quests", {}):
        del udata["active_quests"][quest_id]
        save_guild_data(gid, guild_data, interaction.guild.name)
        await interaction.response.send_message(f"✅ Removed quest `{quest_id}` from {user.mention}.", ephemeral=True)
    else:
        await interaction.response.send_message(f"User does not have quest `{quest_id}`.", ephemeral=True)

@quest_manage_group.command(name="list", description="List a user's active quests.")
@app_commands.describe(user="User to view quests for.")
@app_commands.checks.has_permissions(administrator=True)
async def quest_list_slash(interaction: discord.Interaction, user: discord.Member):
    if not interaction.guild:
        await interaction.response.send_message("Server only.", ephemeral=True)
        return
    gid = str(interaction.guild.id)
    guild_data = load_guild_data(gid, interaction.guild.name)
    udata = get_user_data_block(gid, str(user.id), guild_data)
    active_quests = udata.get("active_quests", {})
    if not active_quests:
        await interaction.response.send_message(f"{user.mention} has no active quests.", ephemeral=True)
        return
    lines = []
    for qid, prog in active_quests.items():
        qdef = QUEST_DEFINITIONS.get(qid)
        if not qdef:
            continue
        progress = prog.get("progress", 0)
        target = qdef.get("target_count", qdef.get("target", 1))
        lines.append(f"`{qid}`: {qdef['title']} ({progress}/{target})")
    await interaction.response.send_message("\n".join(lines), ephemeral=True)

bot.tree.add_command(quest_manage_group)
# ...existing code...

# --- Update update_quest_progress to support new quest types ---
# (Add handling for ping_bot, view_leaderboard, view_inventory, steal_attempt, collect_total, catch_variety)
# ...existing code...
