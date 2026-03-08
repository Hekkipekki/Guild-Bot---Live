import time
import discord
import config

from data.signup_store import load_signups, save_signups, get_message_signup


def get_button_emoji(name: str):
    emoji_map = getattr(config, "BUTTON_EMOJIS", {})
    value = emoji_map.get(name)

    if not value:
        return None

    try:
        return discord.PartialEmoji.from_str(value)
    except Exception:
        return None


def rebuild_roster(users: dict) -> dict:
    role_signed = {"Tank": [], "Healer": [], "DPS": []}
    bench = []
    late = []
    tentative = []
    absence = []

    sorted_users = sorted(users.items(), key=lambda item: item[1].get("timestamp", 0))

    for user_id, info in sorted_users:
        status = info.get("status", "sign")
        role = info.get("role", "DPS")

        display_role = "DPS" if role in ("Melee", "Ranged") else role

        if status == "sign":
            role_signed[display_role].append((user_id, info))
        elif status == "bench":
            bench.append((user_id, info))
        elif status == "late":
            late.append((user_id, info))
        elif status == "tentative":
            tentative.append((user_id, info))
        elif status == "absence":
            absence.append((user_id, info))

    final_roles = {"Tank": [], "Healer": [], "DPS": []}
    final_bench = list(bench)

    for role in final_roles:
        signed_list = role_signed[role]
        limit = config.ROLE_LIMITS.get(role, len(signed_list))

        final_roles[role] = signed_list[:limit]

        overflow = signed_list[limit:]
        for overflow_user_id, overflow_info in overflow:
            overflow_info["status"] = "bench"
            final_bench.append((overflow_user_id, overflow_info))

    return {
        "roles": final_roles,
        "bench": final_bench,
        "late": late,
        "tentative": tentative,
        "absence": absence,
    }


def format_player_line(user_id: str, info: dict) -> str:
    spec = info.get("spec", "Unknown")
    emoji = config.SPEC_EMOJIS.get(spec, "")
    return f"{emoji} <@{user_id}>" if emoji else f"<@{user_id}>"


def build_signup_embed(title: str, description: str, signup: dict) -> discord.Embed:
    users = signup.get("users", {})
    roster = rebuild_roster(users)

    embed = discord.Embed(
        title=title,
        color=discord.Color.purple(),
    )

    leader_text = signup.get("leader", "Hekkipekki / Rhegaran")
    start_ts = signup.get("start_ts")

    tanks = roster["roles"]["Tank"]
    healers = roster["roles"]["Healer"]
    dps = roster["roles"]["DPS"]

    melee_count = sum(
        1 for _, info in users.items()
        if info.get("status") == "sign" and info.get("role") == "Melee"
    )
    ranged_count = sum(
        1 for _, info in users.items()
        if info.get("status") == "sign" and info.get("role") == "Ranged"
    )
    total_signed = len(tanks) + len(healers) + len(dps)

    tank_value = "\n".join(format_player_line(user_id, info) for user_id, info in tanks) if tanks else "-"
    healer_value = "\n".join(format_player_line(user_id, info) for user_id, info in healers) if healers else "-"
    dps_value = "\n".join(format_player_line(user_id, info) for user_id, info in dps) if dps else "-"

    summary_icons = getattr(config, "SUMMARY_EMOJIS", {})

    countdown_icon = summary_icons.get("Countdown", "⏳")
    absence_icon = summary_icons.get("Absence", "🚫")
    signups_icon = summary_icons.get("Signups", "👥")
    dps_icon = summary_icons.get("DPS", "⚔️")
    tank_icon = summary_icons.get("Tank", "🛡️")
    healer_icon = summary_icons.get("Healer", "➕")
    tentative_icon = summary_icons.get("Tentative", "❔")
    late_icon = summary_icons.get("Late", "🕒")
    calendar_icon = summary_icons.get("Calendar", "📅")
    bench_icon = summary_icons.get("Bench", "🪑")

    embed.description = description

    # Row 1
    embed.add_field(
        name="Leader",
        value=f"🏳️ {leader_text}",
        inline=True,
    )
    embed.add_field(
        name="Signups",
        value=f"{signups_icon} {total_signed}",
        inline=True,
    )
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    # Row 2 - dynamic Discord timestamps
    if start_ts:
        date_value = f"{calendar_icon} <t:{start_ts}:D>"
        time_value = f"🕒 <t:{start_ts}:t>"
        countdown_value = f"{countdown_icon} <t:{start_ts}:R>"
    else:
        date_value = f"{calendar_icon} -"
        time_value = "🕒 -"
        countdown_value = f"{countdown_icon} -"

    embed.add_field(name="Date", value=date_value, inline=True)
    embed.add_field(name="Time", value=time_value, inline=True)
    embed.add_field(name="Countdown", value=countdown_value, inline=True)

    # Spacer
    embed.add_field(name="\u200b", value="\u200b", inline=False)

    # Main roster blocks
    embed.add_field(name=f"{tank_icon} Tanks ({len(tanks)})", value=tank_value, inline=True)
    embed.add_field(name=f"{healer_icon} Healers ({len(healers)})", value=healer_value, inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.add_field(
        name=f"{dps_icon} DPS ({len(dps)}) — Melee {melee_count} / Ranged {ranged_count}",
        value=dps_value,
        inline=False,
    )

    def add_optional_line(label: str, entries: list, icon: str):
        if not entries:
            return
        value = " ".join(format_player_line(user_id, info) for user_id, info in entries)
        embed.add_field(
            name=f"{icon} {label} ({len(entries)})",
            value=value,
            inline=False,
        )

    add_optional_line("Late", roster["late"], late_icon)
    add_optional_line("Tentative", roster["tentative"], tentative_icon)
    add_optional_line("Bench", roster["bench"], bench_icon)
    add_optional_line("Absence", roster["absence"], absence_icon)

    return embed


def update_public_signup_message_data(message_id: int) -> dict:
    data = load_signups()
    signup = get_message_signup(data, message_id)
    return signup["users"]


class ClassSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=class_name, value=class_name)
            for class_name in config.CLASSES
        ]

        super().__init__(
            placeholder="Select your class",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_class = self.values[0]
        parent_message_id = self.view.parent_message_id

        data = load_signups()
        signup = get_message_signup(data, parent_message_id)
        users = signup["users"]

        user_id = str(interaction.user.id)
        users.setdefault(user_id, {})
        users[user_id]["class"] = selected_class
        users[user_id]["spec"] = ""
        users[user_id]["role"] = ""
        users[user_id].setdefault("status", "sign")
        users[user_id].setdefault("timestamp", time.time())

        save_signups(data)

        await interaction.response.edit_message(
            content=f"Class set to **{selected_class}**. Now choose your spec:",
            view=SpecPickerView(
                parent_message_id=parent_message_id,
                selected_class=selected_class
            ),
        )

class SpecSelect(discord.ui.Select):
    def __init__(self, selected_class: str):
        options = [
            discord.SelectOption(label=spec, value=spec)
            for spec in config.CLASS_SPECS[selected_class].keys()
        ]

        super().__init__(
            placeholder=f"Select spec for {selected_class}",
            options=options,
            min_values=1,
            max_values=1,
        )
        self.selected_class = selected_class

    async def callback(self, interaction: discord.Interaction):
        selected_spec = self.values[0]
        selected_class = self.selected_class
        role = config.CLASS_SPECS[selected_class][selected_spec]

        parent_message_id = self.view.parent_message_id

        data = load_signups()
        signup = get_message_signup(data, parent_message_id)
        users = signup["users"]

        user_id = str(interaction.user.id)
        users.setdefault(user_id, {})
        users[user_id]["class"] = selected_class
        users[user_id]["spec"] = selected_spec
        users[user_id]["role"] = role
        users[user_id].setdefault("status", "tentative")
        users[user_id].setdefault("timestamp", time.time())

        title = signup.get("title", "Raid Signup")
        description = signup.get("description", "")
        embed = build_signup_embed(title, description, signup)

        save_signups(data)

        channel = interaction.channel
        if channel is not None:
            try:
                message = await channel.fetch_message(parent_message_id)
                await message.edit(embed=embed, view=SignupView(str(parent_message_id)))
            except discord.NotFound:
                pass

        await interaction.response.edit_message(
            content="\u200b",
            view=None,
        )


class ClassPickerView(discord.ui.View):
    def __init__(self, parent_message_id: int):
        super().__init__(timeout=120)
        self.parent_message_id = parent_message_id
        self.add_item(ClassSelect())


class SpecPickerView(discord.ui.View):
    def __init__(self, parent_message_id: int, selected_class: str):
        super().__init__(timeout=120)
        self.parent_message_id = parent_message_id
        self.add_item(SpecSelect(selected_class=selected_class))


class SignupStatusButton(discord.ui.Button):
    def __init__(
        self,
        *,
        raid_id: str,
        status: str,
        label: str,
        emoji_name: str,
        style: discord.ButtonStyle,
        row: int,
    ):
        super().__init__(
            label=label,
            emoji=get_button_emoji(emoji_name),
            style=style,
            custom_id=f"signup:{status}:{raid_id}",
            row=row,
        )
        self.raid_id = raid_id
        self.status = status

    async def callback(self, interaction: discord.Interaction):
        data = load_signups()
        signup = get_message_signup(data, int(self.raid_id))

        title = signup.get("title", "Raid Signup")
        description = signup.get("description", "")
        users = signup["users"]

        user_id = str(interaction.user.id)
        users.setdefault(user_id, {})

        users[user_id].setdefault("class", "Unknown")
        users[user_id].setdefault("spec", "Unknown")
        users[user_id].setdefault("role", "DPS")
        users[user_id]["status"] = self.status
        users[user_id].setdefault("timestamp", time.time())

        embed = build_signup_embed(title, description, signup)

        save_signups(data)
        await interaction.message.edit(embed=embed, view=SignupView(self.raid_id))

        await interaction.response.defer()

class ClassSpecButton(discord.ui.Button):
    def __init__(self, *, raid_id: str, row: int):
        super().__init__(
            label="Choose Class",
            emoji=get_button_emoji("config"),
            style=discord.ButtonStyle.secondary,
            custom_id=f"signup:classspec:{raid_id}",
            row=row,
        )
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Choose your class:",
            ephemeral=True,
            view=ClassPickerView(parent_message_id=int(self.raid_id)),
        )


class LeaveButton(discord.ui.Button):
    def __init__(self, *, raid_id: str, row: int):
        super().__init__(
            label="Leave",
            emoji=get_button_emoji("leave"),
            style=discord.ButtonStyle.secondary,
            custom_id=f"signup:leave:{raid_id}",
            row=row,
        )
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        data = load_signups()
        signup = get_message_signup(data, int(self.raid_id))

        title = signup.get("title", "Raid Signup")
        description = signup.get("description", "")
        users = signup["users"]

        user_id = str(interaction.user.id)
        if user_id in users:
            del users[user_id]

        embed = build_signup_embed(title, description, signup)

        save_signups(data)
        await interaction.message.edit(embed=embed, view=SignupView(self.raid_id))

        await interaction.response.defer()

class SignupView(discord.ui.View):
    def __init__(self, raid_id: str):
        super().__init__(timeout=None)
        self.raid_id = raid_id

        # Row 1
        self.add_item(
            SignupStatusButton(
                raid_id=raid_id,
                status="sign",
                label="Sign",
                emoji_name="sign",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            SignupStatusButton(
                raid_id=raid_id,
                status="late",
                label="Late",
                emoji_name="late",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            SignupStatusButton(
                raid_id=raid_id,
                status="bench",
                label="Bench",
                emoji_name="bench",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            SignupStatusButton(
                raid_id=raid_id,
                status="tentative",
                label="Tentative",
                emoji_name="tentative",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            SignupStatusButton(
                raid_id=raid_id,
                status="absence",
                label="Absence",
                emoji_name="absence",
                style=discord.ButtonStyle.secondary,
                row=0,
            )
        )

        # Row 2
        self.add_item(
            ClassSpecButton(
                raid_id=raid_id,
                row=1,
            )
        )
        self.add_item(
            LeaveButton(
                raid_id=raid_id,
                row=1,
            )
        )