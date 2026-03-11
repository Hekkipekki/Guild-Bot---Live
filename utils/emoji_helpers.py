import discord
import config


def parse_spec_emoji(spec_name: str):
    raw = config.SPEC_EMOJIS.get(spec_name)
    if not raw:
        return None

    try:
        return discord.PartialEmoji.from_str(raw)
    except Exception:
        return None


def parse_class_emoji(class_name: str):
    raw = getattr(config, "CLASS_EMOJIS", {}).get(class_name)
    if not raw:
        return None

    try:
        return discord.PartialEmoji.from_str(raw)
    except Exception:
        return None
    
def parse_button_emoji(name: str):
    raw = getattr(config, "BUTTON_EMOJIS", {}).get(name)
    if not raw:
        return None

    try:
        return discord.PartialEmoji.from_str(raw)
    except Exception:
        return None