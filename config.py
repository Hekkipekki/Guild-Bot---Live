from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TOKEN = "MTQ0NzY0NjUxMjgxNjQ1NTk0Mg.GFKPTK.hJ198ZaicCW3Qjj4eRDrMJ1r_2kSb6sV7py4yI"  # put your bot token here
WEAKAURAS_CHANNEL_ID = 1423733790907306005

PACKS = {
    "tot_01_06": {
        "label": "ToT Boss 1–6",
        "file": "files/Fojji_-_T1501-06_Throne_of_Thunder-3.0.2.txt",
        "title": "Fojji - Throne of Thunder [01–06]",
        "version": "v3.0.2",
    },
    "tot_07_13": {
        "label": "ToT Boss 7–13",
        "file": "files/Fojji_-_T1507-13_Throne_of_Thunder-3.0.3.txt",
        "title": "Fojji - Throne of Thunder [07–13]",
        "version": "v3.0.3",
    },
    "tot_frames": {
        "label": "ToT Raid Frames",
        "file": "files/Fojji_-_T15Raid_Frame_Throne_of_Thunder-3.0.2.txt",
        "title": "Fojji - Throne of Thunder Raid Frames",
        "version": "v3.0.2",
    },
    "tot_personal_assignments": {
        "label": "ToT Assignments",
        "file": "files/Fojji-ToT-Personal-Assignments[1.0.0].txt",
        "title": "Fojji - ToT Personal Assignments",
        "version": "v1.0.0",
    },
    "tot_assignments": {
        "label": "Fojji - Raid Assignments [TOT][Raid Leader][1.0.1]",
        "file": "files/Fojji - Raid Assignments [TOT][Raid Leader][1.0.1].txt",
        "title": "Fojji - Raid Assignments [ToT] (Raid Leader)",
        "version": "v1.0.1",
    },
    "msv": {
        "label": "Fojji - Mogu'Shan Vaults v1.0.20",
        "file": "files/Fojji-MoguShan-v1.0.20.txt",
        "title": "Fojji - Mogu'Shan Vaults",
        "version": "v1.0.20",
    },
    "hof": {
        "label": "Fojji - Heart of Fear v1.0.10",
        "file": "files/Fojji-Heart-of-Fear-v1.0.10.txt",
        "title": "Fojji - Heart of Fear",
        "version": "v1.0.10",
    },
    "toes": {
        "label": "Fojji - Terrace of Endless Springs v3.0.9",
        "file": "files/Fojji-Terrace-of-Endless-Springs-v3.0.9.txt",
        "title": "Fojji - Terrace of Endless Springs",
        "version": "v3.0.9",
    },
}

CLASSES = [
    "Death Knight",
    "Warrior",
    "Druid",
    "Paladin",
    "Monk",
    "Priest",
    "Mage",
    "Warlock",
    "Hunter",
    "Rogue",
    "Shaman",
]

CLASS_SPECS = {
    "Death Knight": {
        "Blood": "Tank",
        "FrostDK": "Melee",
        "Unholy": "Melee",
    },
    "Warrior": {
        "Arms": "Melee",
        "Fury": "Melee",
        "ProtectionWarrior": "Tank",
    },
    "Druid": {
        "Balance": "Ranged",
        "Feral": "Melee",
        "Guardian": "Tank",
        "RestorationDruid": "Healer",
    },
    "Paladin": {
        "HolyPaladin": "Healer",
        "ProtectionPaladin": "Tank",
        "Retribution": "Melee",
    },
    "Monk": {
        "Brewmaster": "Tank",
        "Mistweaver": "Healer",
        "Windwalker": "Melee",
    },
    "Priest": {
        "Discipline": "Healer",
        "HolyPriest": "Healer",
        "Shadow": "Ranged",
    },
    "Mage": {
        "Arcane": "Ranged",
        "Fire": "Ranged",
        "Frost": "Ranged",
    },
    "Warlock": {
        "Affliction": "Ranged",
        "Demonology": "Ranged",
        "Destruction": "Ranged",
    },
    "Hunter": {
        "Beast Mastery": "Ranged",
        "Marksmanship": "Ranged",
        "Survival": "Ranged",
    },
    "Rogue": {
        "Assassination": "Melee",
        "Combat": "Melee",
        "Subtlety": "Melee",
    },
    "Shaman": {
        "Elemental": "Ranged",
        "Enhancement": "Melee",
        "RestorationShaman": "Healer",
    },
}

ROLE_LIMITS = {
    "Tank": 2,
    "Healer": 3,
    "DPS": 9,
}

SPEC_EMOJIS = {
    "Blood": "<:Blood:1480262449713385514>",
    "Frost": "<:Frost:1480262252316856470>",
    "Unholy": "<:Unholy:1480262445695238276>",

    "Arms": "<:Arms:1480262401281753119>",
    "Fury": "<:Fury:1480262411973033984>",
    "ProtectionWarrior": "<:ProtectionWarrior:1480262388639993967>",

    "Balance": "<:Balance:1480262444000477245>",
    "Feral": "<:Feral:1480262440313946285>",
    "Guardian": "<:Guardian:1480262442067165215>",
    "RestorationDruid": "<:RestorationDruid:1480262438736892075>",

    "HolyPaladin": "<:HolyPaladin:1480262327034052761>",
    "ProtectionPaladin": "<:ProtectionPaladin:1480262329684721807>",
    "Retribution": "<:Retribution:1480262333275181199>",

    "Brewmaster": "<:Brewmaster:1480262251033268365>",
    "Mistweaver": "<:Mistweaver:1480262249162739946>",
    "Windwalker": "<:Windwalker:1480262246792953926>",

    "Discipline": "<:Discipline:1480262338450817025>",
    "HolyPriest": "<:HolyPriest:1480262340720201909>",
    "Shadow": "<:Shadow:1480262324974649435>",

    "Arcane": "<:Arcane:1480262255286288584>",
    "Fire": "<:Fire:1480262253738594507>",
    "FrostDK": "<:FrostDK:1480262447456588057>",

    "Affliction": "<:Affliction:1480262334541725858>",
    "Demonology": "<:Demonology:1480262396433137846>",
    "Destruction": "<:Destruction:1480262398400008404>",

    "Beast Mastery": "<:BeastMastery:1480262451814596860>",
    "Marksmanship": "<:Marksmanship:1480262453563494612>",
    "Survival": "<:Survival:1480262455711105188>",

    "Assassination": "<:Assassination:1480262257726512248>",
    "Combat": "<:Combat:1480262256540254464>",
    "Subtlety": "<:Subtlety:1480262260029915288>",

    "Elemental": "<:Elemental:1480262394990301396>",
    "Enhancement": "<:Enhancement:1480262393014653061>",
    "RestorationShaman": "<:RestorationShaman:1480262390586015814>",
}

SUMMARY_EMOJIS = {
    "Countdown": "<:Countdown:1480262039753588919>",
    "Absence": "<:Absence:1480262041284382790>",
    "Signups": "<:Signups:1480262042953715825>",
    "DPS": "<:DPS:1480262044497346712>",
    "Tank": "<:Tank:1480262046036787260>",
    "Healer": "<:Healer:1480262047483822347>",
    "Tentative": "<:Tentative:1480262159031210115>",
    "Late": "<:Late:1480262058648932478>",
    "Calendar": "<:Calendar:1480262061090017300>",
    "Bench": "<:Bench:1480262055188758799>",
}

BUTTON_EMOJIS = {
    "sign": "<:Sign:1480262051644313905>",
    "late": "<:Late:1480262058648932478>",
    "bench": "<:Bench:1480262055188758799>",
    "tentative": "<:Tentative:1480262159031210115>",
    "absence": "<:Absence:1480262041284382790>",
    "config": "<:Config:1480262049270333442>",
    "leave": "<:Leave:1480262053632540682>",
}