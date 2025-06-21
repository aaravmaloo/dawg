import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import asyncio
import os
import json
from datetime import datetime, timezone # For UTC timestamps

# ----------------------------------------------------------------------------------
BOT_TOKEN = "MTM4MDc4NjE2NTAzMjAyNjIwMg.GQfUgr.5Izsz8zwEtuVqNHdMVnkd9OLByQQ9h-dBQGgAE" # REPLACE THIS
# ----------------------------------------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix="!unused!", intents=intents)

# --- Default Global Configuration (used if per-guild settings are missing/new guild) ---
DEFAULT_MIN_SPAWN_SECONDS = 120
DEFAULT_MAX_SPAWN_SECONDS = 300
DEFAULT_POST_CATCH_SPAWN_SECONDS = 30

CAUGHT_DOG_EMOJI_FALLBACK = "🦴"
DOG_IMAGE_PATH_TEMPLATE = os.path.join("src", "imgs", "{image_name}")
DATA_DIR = os.path.join("data")

DOG_TYPES = {
    "normal_dog": {
        "display_name": "Normal Dog",
        "emoji_name": "normal_dog_img",
        "emoji_id": "1384534131970412594",
        "image_name": "dog.png"
    }
}
CURRENT_SPAWN_TYPE_KEY = "normal_dog"
active_dog_spawns = {} # Key: channel_id, Value: { "dog_type": key, "guild_id": id }


# --- Helper Functions for Per-Guild Data Handling ---
def get_guild_data_file_path(guild_id):
    return os.path.join(DATA_DIR, f"guild_{guild_id}.json")

def load_guild_data(guild_id, guild_name_for_init="Unknown Server"):
    path = get_guild_data_file_path(guild_id)
    current_timestamp = int(datetime.now(timezone.utc).timestamp())
    default_data = {
        "settings": {
            "min_spawn_seconds": DEFAULT_MIN_SPAWN_SECONDS,
            "max_spawn_seconds": DEFAULT_MAX_SPAWN_SECONDS,
            "post_catch_spawn_seconds": DEFAULT_POST_CATCH_SPAWN_SECONDS,
            "server_name_for_reference": guild_name_for_init
        },
        "spawn_state": {
            # Start eligible to spawn almost immediately (or after a short delay)
            "next_eligible_spawn_timestamp": current_timestamp + random.randint(10, 30),
            "is_in_post_catch_cooldown": False
        },
        "user_inventories": {}
    }
    if os.path.exists(path):
        try:
            with open(path, 'r') as f: content = f.read()
            if not content.strip(): return default_data
            data = json.loads(content)
            # Ensure all keys exist, merge defaults for missing parts
            if "settings" not in data: data["settings"] = default_data["settings"].copy()
            else:
                data["settings"].setdefault("min_spawn_seconds", DEFAULT_MIN_SPAWN_SECONDS)
                data["settings"].setdefault("max_spawn_seconds", DEFAULT_MAX_SPAWN_SECONDS)
                data["settings"].setdefault("post_catch_spawn_seconds", DEFAULT_POST_CATCH_SPAWN_SECONDS)
                data["settings"].setdefault("server_name_for_reference", guild_name_for_init)
            if "spawn_state" not in data: data["spawn_state"] = default_data["spawn_state"].copy()
            else:
                data["spawn_state"].setdefault("next_eligible_spawn_timestamp", current_timestamp + random.randint(min(data["settings"]["min_spawn_seconds"],60), data["settings"]["min_spawn_seconds"] )) # Sensible default if missing
                data["spawn_state"].setdefault("is_in_post_catch_cooldown", False)
            if "user_inventories" not in data: data["user_inventories"] = {}
            return data
        except Exception as e:
            print(f"[{datetime.now()}] Error loading data for guild {guild_id} from {path}: {e}")
            return default_data
    return default_data

def save_guild_data(guild_id, data, guild_name_for_ref=""):
    if not os.path.exists(DATA_DIR):
        try: os.makedirs(DATA_DIR)
        except Exception as e: print(f"[{datetime.now()}] Error creating data dir: {e}"); return False
    
    if guild_name_for_ref: # Update server name if provided
        data.setdefault("settings", {}).update({"server_name_for_reference": guild_name_for_ref})

    path = get_guild_data_file_path(guild_id)
    try:
        with open(path, 'w') as f: json.dump(data, f, indent=4)
        # print(f"[{datetime.now()}] Saved data for guild {guild_id} ('{data.get('settings',{}).get('server_name_for_reference','Unknown')}').")
        return True
    except Exception as e: print(f"[{datetime.now()}] Error saving data for guild {guild_id}: {e}"); return False

def get_user_inventory(guild_id, user_id): # Same as before
    guild_data = load_guild_data(guild_id)
    user_inventories = guild_data.get("user_inventories", {})
    user_id_str = str(user_id)
    if user_id_str not in user_inventories: user_inventories[user_id_str] = {}
    for key in DOG_TYPES:
        if key not in user_inventories[user_id_str]: user_inventories[user_id_str][key] = 0
    return user_inventories.get(user_id_str, {})

# --- TASKS.LOOP FUNCTION (Global Poller for Per-Guild Spawns) ---
@tasks.loop(seconds=15) # How often to check all guilds (e.g., every 15-30 seconds)
async def per_guild_spawn_checker_task():
    print(f"[{datetime.now()}] PER_GUILD_SPAWN_CHECKER: Running global check for {len(bot.guilds)} guilds.")
    current_timestamp = int(datetime.now(timezone.utc).timestamp())

    for guild in bot.guilds:
        guild_data = load_guild_data(guild.id, guild.name) # Load current data
        settings = guild_data["settings"]
        spawn_state = guild_data["spawn_state"]

        # print(f"[{datetime.now()}] Checking Guild: {guild.name}, Next Spawn At: {datetime.fromtimestamp(spawn_state['next_eligible_spawn_timestamp'], timezone.utc)}, Now: {datetime.fromtimestamp(current_timestamp, timezone.utc)}")

        if current_timestamp >= spawn_state["next_eligible_spawn_timestamp"]:
            print(f"[{datetime.now()}] Guild '{guild.name}' is eligible for spawn (time met).")
            eligible_channels_in_guild = []
            for channel in guild.text_channels:
                permissions = channel.permissions_for(guild.me)
                if permissions.send_messages and permissions.attach_files and \
                   not active_dog_spawns.get(channel.id): # Check if dog already spawned by this bot in this channel
                    eligible_channels_in_guild.append(channel)
            
            if eligible_channels_in_guild:
                chosen_channel = random.choice(eligible_channels_in_guild)
                print(f"[{datetime.now()}] Attempting to spawn in '{guild.name}' -> #{chosen_channel.name}")
                try:
                    dog_type_to_spawn = CURRENT_SPAWN_TYPE_KEY
                    dog_info = DOG_TYPES[dog_type_to_spawn]
                    dog_image_path = DOG_IMAGE_PATH_TEMPLATE.format(image_name=dog_info["image_name"])
                    spawn_message_text = f"A {dog_info['display_name']} has appeared in {guild.name}! Type `dog` to catch it!"
                    
                    if os.path.exists(dog_image_path):
                        await chosen_channel.send(spawn_message_text, file=discord.File(dog_image_path))
                    else:
                        await chosen_channel.send(f"{spawn_message_text}\n(Picture missing!)")
                    
                    active_dog_spawns[chosen_channel.id] = {"dog_type": dog_type_to_spawn, "guild_id": guild.id}
                    print(f"[{datetime.now()}] Spawn successful in '{guild.name}' -> #{chosen_channel.name}.")

                    # Update this guild's next spawn time
                    min_s = settings["min_spawn_seconds"]
                    max_s = settings["max_spawn_seconds"]
                    next_delay = random.randint(min_s, max_s)
                    spawn_state["next_eligible_spawn_timestamp"] = current_timestamp + next_delay
                    spawn_state["is_in_post_catch_cooldown"] = False # Reset cooldown if it was in one
                    save_guild_data(guild.id, guild_data, guild.name)
                    print(f"[{datetime.now()}] Guild '{guild.name}' next NORMAL spawn in {next_delay}s.")

                except Exception as e:
                    print(f"[{datetime.now()}] Error spawning in guild {guild.name}: {e}")
            # else: print(f"[{datetime.now()}] No eligible channels found in '{guild.name}' despite being time-eligible.")
        # else: print(f"[{datetime.now()}] Guild '{guild.name}' not yet eligible for spawn.")
    # print(f"[{datetime.now()}] PER_GUILD_SPAWN_CHECKER: Cycle finished.")


# --- Bot Events ---
@bot.event
async def on_ready():
    print(f"[{datetime.now()}] ON_READY: Bot '{bot.user.name}' has connected!")
    if not os.path.exists(DATA_DIR):
        try: os.makedirs(DATA_DIR)
        except Exception as e: print(f"[{datetime.now()}] ON_READY: Error creating data dir: {e}")

    for guild in bot.guilds: # Ensure all guilds have a data file initialized
        guild_data = load_guild_data(guild.id, guild.name)
        save_guild_data(guild.id, guild_data, guild.name) # Save to create/update
        print(f"[{datetime.now()}] Initialized/checked data for guild: {guild.name} (ID: {guild.id})")
        # Initialize next_eligible_spawn_timestamp if it's 0 (first run for this guild)
        if guild_data["spawn_state"]["next_eligible_spawn_timestamp"] == 0 :
            current_ts = int(datetime.now(timezone.utc).timestamp())
            initial_delay = random.randint(min(10, guild_data["settings"]["min_spawn_seconds"]), guild_data["settings"]["min_spawn_seconds"])
            guild_data["spawn_state"]["next_eligible_spawn_timestamp"] = current_ts + initial_delay
            save_guild_data(guild.id, guild_data, guild.name)
            print(f"[{datetime.now()}] Set initial spawn eligibility for {guild.name} in {initial_delay}s.")


    print(f"[{datetime.now()}] ON_READY: Attempting GLOBAL command sync...")
    try:
        synced_commands = await bot.tree.sync()
        print(f"[{datetime.now()}] ON_READY: Synced {len(synced_commands)} commands globally.")
    except Exception as e: print(f"[{datetime.now()}] ON_READY: Error global command sync: {e}")

    if not per_guild_spawn_checker_task.is_running():
        print(f"[{datetime.now()}] ON_READY: Starting per-guild spawn check loop...")
        per_guild_spawn_checker_task.start()

@bot.event
async def on_guild_join(guild):
    print(f"[{datetime.now()}] Joined new guild: {guild.name} (ID: {guild.id})")
    guild_data = load_guild_data(guild.id, guild.name) # Initialize with defaults
    current_ts = int(datetime.now(timezone.utc).timestamp())
    initial_delay = random.randint(min(10, guild_data["settings"]["min_spawn_seconds"]), guild_data["settings"]["min_spawn_seconds"])
    guild_data["spawn_state"]["next_eligible_spawn_timestamp"] = current_ts + initial_delay # Set initial spawn time
    save_guild_data(guild.id, guild_data, guild.name) # Save to create file
    print(f"[{datetime.now()}] Initialized data for new guild {guild.name}. Next spawn check relevant in {initial_delay}s.")


@bot.event
async def on_message(message):
    if message.author == bot.user or not message.guild: return

    if message.content.lower() == "dog":
        channel_id = message.channel.id
        spawn_info = active_dog_spawns.get(channel_id) # Now a dict

        if spawn_info and spawn_info["guild_id"] == message.guild.id:
            spawned_dog_type_key = spawn_info["dog_type"]
            guild_id_of_spawn = spawn_info["guild_id"]
            
            try:
                print(f"[{datetime.now()}] CATCH EVENT: '{message.author.name}' catching in guild {message.guild.name}.")
                del active_dog_spawns[channel_id] # Dog is caught

                # Update user inventory (same as before)
                user_id_str = str(message.author.id)
                guild_data = load_guild_data(guild_id_of_spawn, message.guild.name)
                inventories = guild_data.setdefault("user_inventories", {})
                user_inv = inventories.setdefault(user_id_str, {})
                user_inv[spawned_dog_type_key] = user_inv.get(spawned_dog_type_key, 0) + 1
                
                # Set this guild for a quick post-catch spawn
                current_timestamp = int(datetime.now(timezone.utc).timestamp())
                post_catch_delay = guild_data["settings"].get("post_catch_spawn_seconds", DEFAULT_POST_CATCH_SPAWN_SECONDS)
                
                guild_data["spawn_state"]["next_eligible_spawn_timestamp"] = current_timestamp + post_catch_delay
                guild_data["spawn_state"]["is_in_post_catch_cooldown"] = True # Mark it
                
                save_guild_data(guild_id_of_spawn, guild_data, message.guild.name)
                print(f"[{datetime.now()}] Guild '{message.guild.name}' set for post-catch spawn in {post_catch_delay}s.")

                dog_info = DOG_TYPES[spawned_dog_type_key]
                emoji_str = f"<:{dog_info['emoji_name']}:{dog_info['emoji_id']}>" if dog_info.get('emoji_id') else CAUGHT_DOG_EMOJI_FALLBACK
                await message.channel.send(f"Good catch, {message.author.mention}! You got {dog_info['display_name']}! {emoji_str}")

            except Exception as e:
                print(f"[{datetime.now()}] CATCH EVENT: Error: {e}"); await message.channel.send("Woof! Error during catch.")

# --- Slash Commands (inventory is same, changespawntimings updated) ---
@bot.tree.command(name="inventory", description="Shows your caught dog inventory.") # Same as before
async def inventory_slash(interaction: discord.Interaction):
    if not interaction.guild: await interaction.response.send_message("Server only.", ephemeral=True); return
    user_inv = get_user_inventory(interaction.guild.id, interaction.user.id)
    if not user_inv or all(count == 0 for count in user_inv.values()):
        await interaction.response.send_message("Empty inventory.", ephemeral=True); return
    embed = discord.Embed(title=f"{interaction.user.display_name}'s Inventory", color=discord.Color.green())
    display = [f"<:{DOG_TYPES[key]['emoji_name']}:{DOG_TYPES[key]['emoji_id']}> {DOG_TYPES[key]['display_name']}: **{count}**" if DOG_TYPES.get(key,{}).get('emoji_id') else f"{CAUGHT_DOG_EMOJI_FALLBACK} {DOG_TYPES.get(key,{}).get('display_name','Unknown')}: **{count}**"
               for key, count in user_inv.items() if count > 0]
    embed.description = "\n".join(display) if display else "No dogs caught yet!"
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="changespawntimings", description="Admin: Set THIS server's min/max/post-catch spawn times (seconds).")
@app_commands.describe(
    min_seconds="Min seconds between normal spawns (e.g., 120)",
    max_seconds="Max seconds between normal spawns (e.g., 300)",
    post_catch_seconds="Seconds for a quick respawn after a catch (e.g., 30)"
)
@app_commands.checks.has_permissions(administrator=True)
async def change_spawn_timings_slash(interaction: discord.Interaction, min_seconds: int, max_seconds: int, post_catch_seconds: int):
    if not interaction.guild: await interaction.response.send_message("Server only.", ephemeral=True); return

    if not (10 <= min_seconds < max_seconds <= 7200): # Min 10s, Max 2hrs, min < max
        await interaction.response.send_message("Invalid normal timings. Min:10-7199s, Max:(Min+1)-7200s.", ephemeral=True); return
    if not (5 <= post_catch_seconds <= 600): # Post catch 5s to 10min
        await interaction.response.send_message("Invalid post-catch timing. Must be between 5 and 600 seconds.", ephemeral=True); return

    guild_id_str = str(interaction.guild.id)
    guild_data = load_guild_data(guild_id_str, interaction.guild.name)
    
    guild_data["settings"]["min_spawn_seconds"] = min_seconds
    guild_data["settings"]["max_spawn_seconds"] = max_seconds
    guild_data["settings"]["post_catch_spawn_seconds"] = post_catch_seconds
    
    # Optional: If not in post-catch cooldown, immediately set next spawn for this guild
    current_timestamp = int(datetime.now(timezone.utc).timestamp())
    if not guild_data["spawn_state"]["is_in_post_catch_cooldown"]:
        next_delay = random.randint(min_seconds, max_seconds)
        guild_data["spawn_state"]["next_eligible_spawn_timestamp"] = current_timestamp + next_delay
        print(f"[{datetime.now()}] Timings changed for '{interaction.guild.name}'. Next normal spawn in {next_delay}s.")
    else:
        print(f"[{datetime.now()}] Timings changed for '{interaction.guild.name}'. Currently in post-catch cooldown, new normal timings will apply after.")


    if save_guild_data(guild_id_str, guild_data, interaction.guild.name):
        await interaction.response.send_message(f"✅ Spawn timings for '{interaction.guild.name}' updated:\n"
                                               f"Normal: {min_seconds}s - {max_seconds}s\n"
                                               f"Post-Catch: {post_catch_seconds}s.")
    else:
        await interaction.response.send_message("❌ Error saving new spawn timings.", ephemeral=True)

@change_spawn_timings_slash.error # Same error handler
async def change_spawn_timings_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions): await interaction.response.send_message("⛔ Admins only.", ephemeral=True)
    else: await interaction.response.send_message(f"🤔 Error: {type(error).__name__}", ephemeral=True); print(f"Err: {error}")

# --- MAIN RUN ---
if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_SUPER_SECRET_BOT_TOKEN_HERE": print("ERROR: Set BOT_TOKEN.")
    else:
        try: bot.run(BOT_TOKEN)
        except Exception as e: print(f"[{datetime.now()}] Bot run error: {e}"); import traceback; traceback.print_exc()