import dotenv
import os

loaded = dotenv.load_dotenv(r'C:\Users\Aarav Maloo\Desktop\dog bot\src\secret.env')
print(f"dotenv.load_dotenv() returned: {loaded}") # Should be True if .env was found

BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)