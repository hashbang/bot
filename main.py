from bot import Bot
from bot.plugins import DebugPlugin, ScriptStarterPlugin
import json

if __name__ == "__main__":
    try:
        config = json.loads(open("config.json").read())

        bot = Bot(config)
        bot.loadPlugin(ScriptStarterPlugin(config['plugins']))
        bot.loop()

        print("Regular Exit")
    except:
        print("Exceptional exit:")
        raise
