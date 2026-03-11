import random

import config
from data.signup_store import load_signups, save_signups
from logic.embed_builder import build_signup_embed
from views.signup_views import SignupView


FAKE_NAMES = [
    "Thorgrim", "Leafhealz", "Shadowzap", "Bonkadin", "Totemlord",
    "Frostzug", "Moonbeef", "Sneakstab", "Pyroblastz", "Soulrot",
    "Mendrina", "Bearjuice", "Shockbot", "Arrowqt", "Smitey",
    "Hexella", "Clawbert", "Shieldbro", "Dotsdot", "Windbonk",
    "Holytoast", "Darkmoo", "Stonepaw", "Critlord", "Glimmer",
]


def build_signup_payload(
    *,
    title: str,
    description: str,
    leader: str,
    start_ts: int,
    channel_id: int,
    users: dict | None = None,
) -> dict:
    return {
        "title": title,
        "description": description,
        "leader": leader,
        "start_ts": start_ts,
        "channel_id": channel_id,
        "users": users or {},
        "expected_players": [
            str(player_id)
            for player_id in getattr(config, "DEFAULT_EXPECTED_PLAYERS", [])
        ],
        "missing_signup_reminders_sent": {
            "2880": False,
            "1440": False,
        },
        "signed_player_reminders_sent": {
            "60": False,
        },
    }


def build_fake_users() -> dict:
    tanks = [
        ("Death Knight", "Blood", "Tank"),
        ("Warrior", "ProtectionWarrior", "Tank"),
        ("Druid", "Guardian", "Tank"),
        ("Paladin", "ProtectionPaladin", "Tank"),
        ("Monk", "Brewmaster", "Tank"),
    ]

    healers = [
        ("Paladin", "HolyPaladin", "Healer"),
        ("Druid", "RestorationDruid", "Healer"),
        ("Priest", "Discipline", "Healer"),
        ("Priest", "HolyPriest", "Healer"),
        ("Shaman", "RestorationShaman", "Healer"),
        ("Monk", "Mistweaver", "Healer"),
    ]

    dps = [
        ("Warrior", "Arms", "Melee"),
        ("Warrior", "Fury", "Melee"),
        ("Druid", "Balance", "Ranged"),
        ("Druid", "Feral", "Melee"),
        ("Paladin", "Retribution", "Melee"),
        ("Monk", "Windwalker", "Melee"),
        ("Priest", "Shadow", "Ranged"),
        ("Mage", "Arcane", "Ranged"),
        ("Mage", "Fire", "Ranged"),
        ("Mage", "Frost", "Ranged"),
        ("Warlock", "Affliction", "Ranged"),
        ("Warlock", "Demonology", "Ranged"),
        ("Warlock", "Destruction", "Ranged"),
        ("Hunter", "Beast Mastery", "Ranged"),
        ("Hunter", "Marksmanship", "Ranged"),
        ("Hunter", "Survival", "Ranged"),
        ("Rogue", "Assassination", "Melee"),
        ("Rogue", "Combat", "Melee"),
        ("Rogue", "Subtlety", "Melee"),
        ("Shaman", "Elemental", "Ranged"),
        ("Shaman", "Enhancement", "Melee"),
        ("Death Knight", "FrostDK", "Melee"),
        ("Death Knight", "Unholy", "Melee"),
    ]

    tank_count = random.randint(1, 2)
    healer_count = random.randint(2, 3)
    dps_count = random.randint(8, 9)

    selected_tanks = random.sample(tanks, k=tank_count)
    selected_healers = random.sample(healers, k=healer_count)
    selected_dps = random.sample(dps, k=dps_count)

    selected_players = (
        [("sign", p) for p in selected_tanks]
        + [("sign", p) for p in selected_healers]
        + [("sign", p) for p in selected_dps]
    )

    extra_statuses = ["late", "tentative", "absence", "bench"]
    extra_pool = random.sample(dps + healers + tanks, k=4)

    selected_players += list(zip(extra_statuses, extra_pool))

    used_names = random.sample(FAKE_NAMES, k=len(selected_players))

    users = {}
    now = __import__("time").time()

    for i, (status, (player_class, spec, role)) in enumerate(selected_players):
        fake_user_id = f"demo_{i}"
        users[fake_user_id] = {
            "display_name": used_names[i],
            "class": player_class,
            "spec": spec,
            "role": role,
            "status": status,
            "timestamp": now + i,
        }

    return users


async def send_signup_message(ctx, signup: dict) -> None:
    embed = build_signup_embed(signup["title"], signup["description"], signup)

    message = await ctx.send(embed=embed)
    await message.edit(view=SignupView(str(message.id)))

    data = load_signups()
    data[str(message.id)] = signup
    save_signups(data)