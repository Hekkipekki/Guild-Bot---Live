from pathlib import Path

TEST_GUILD_ID = 1423706462773051542
RAID_CONTROL_USER_IDS = [
    141881090913599488,  # Hekkipekki
    321966396864987137,  # Jensen
    733947209845833730,  # Frika
    248796420880990208,  # Turit
]
WEAKAURAS_CHANNEL_ID = 1423733790907306005

BASE_DIR = Path(__file__).resolve().parent

try:
    from secrets_local import TOKEN
except ImportError:
    TOKEN = None

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
    # Death Knight
    "Blood": "<:Blood:1481697240304324618>",
    "FrostDK": "<:FrostDK:1481697312488292506>",
    "Unholy": "<:Unholy:1481697310923690118>",

    # Druid
    "Balance": "<:Balance:1481697309292105971>",
    "Feral": "<:Feral:1481697307731693789>",
    "Guardian": "<:Guardian:1481697237263188039>",
    "RestorationDruid": "<:RestorationDruid:1481697306368806913>",

    # Hunter
    "Beast Mastery": "<:BeastMastery:1481697302358786088>",
    "BeastMastery": "<:BeastMastery:1481697302358786088>",  # alias
    "Marksmanship": "<:Marksmanship:1481697303692706002>",
    "Survival": "<:Survival:1481697304699469916>",

    # Mage
    "Arcane": "<:Arcane:1481697276509290718>",
    "Fire": "<:Fire:1481697274919915623>",
    "Frost": "<:Frost:1481697273250316288>",

    # Monk
    "Brewmaster": "<:Brewmaster:1481697271644164208>",
    "Mistweaver": "<:Mistweaver:1481697270176153630>",
    "Windwalker": "<:Windwalker:1481697268460683390>",

    # Paladin
    "HolyPaladin": "<:HolyPaladin:1481697282209349633>",
    "ProtectionPaladin": "<:ProtectionPaladin:1481697233106898965>",
    "Retribution": "<:Retribution:1481697283320975593>",

    # Priest
    "Discipline": "<:Discipline:1481697278128291972>",
    "HolyPriest": "<:HolyPriest:1481697279525130333>",
    "Shadow": "<:Shadow:1481697280724570243>",

    # Rogue
    "Assassination": "<:Assassination:1481697265138663566>",
    "Combat": "<:Combat:1481697263418867855>",
    "Subtlety": "<:Sublety:1481697267202134217>",
    "Sublety": "<:Sublety:1481697267202134217>",  # alias

    # Shaman
    "Elemental": "<:Elemental:1481697300869808320>",
    "Enhancement": "<:Enmhancement:1481697299645337691>",
    "Enmhancement": "<:Enmhancement:1481697299645337691>",  # alias
    "RestorationShaman": "<:RestorationShaman:1481697298118344827>",

    # Warlock
    "Affliction": "<:Affliction:1481697284512022769>",
    "Demonology": "<:Demonology:1481697285724442768>",
    "Destruction": "<:Destruction:1481697286886265114>",

    # Warrior
    "Arms": "<:Arms:1481697295404761169>",
    "Fury": "<:Fury:1481697296688091311>",
    "ProtectionWarrior": "<:ProtectionWarrior:1481697241839439932>",
}

CLASS_EMOJIS = {
    "Death Knight": "<:DEATHKNIGHT:1481697220129591326>",
    "Warrior": "<:WARRIOR:1481697230766477484>",
    "Druid": "<:DRUID:1481697221484482691>",
    "Paladin": "<:PALADIN:1481697223669452870>",
    "Monk": "<:MONK:1481697218410057900>",
    "Priest": "<:PRIEST:1481697224982532266>",
    "Mage": "<:MAGE:1481697231781367808>",
    "Warlock": "<:WARLOCK:1481697229390741525>",
    "Hunter": "<:HUNTER:1481697222629265438>",
    "Rogue": "<:ROGUE:1481697226454728734>",
    "Shaman": "<:SHAMAN:1481697228497354955>",
}

SUMMARY_EMOJIS = {
    "Countdown": "<:Countdown:1481697255172870186>",
    "Absence": "<:Absence:1481697256657780877>",
    "Signups": "<:Signups:1481697257811087443>",
    "DPS": "<:DPS:1481697259501523007>",
    "Tank": "<:Tank:1481697260751290579>",
    "Healer": "<:Healer:1481697262227689492>",
    "Tentative": "<:Tentative:1481697250408267927>",
    "Late": "<:Late:1481697251838525654>",
    "Calendar": "<:Calendar:1481697253910511848>",
    "Bench": "<:Bench:1481697248093143235>",
}

BUTTON_EMOJIS = {
    "sign": "<:Sign:1481697245085831350>",
    "late": "<:Late:1481697251838525654>",
    "bench": "<:Bench:1481697248093143235>",
    "tentative": "<:Tentative:1481697250408267927>",
    "absence": "<:Absence:1481697256657780877>",
    "config": "<:Config:1481697243642724352>",
    "leave": "<:Leave:1481697246507700264>",
}

DEFAULT_EXPECTED_PLAYERS = [
    141881090913599488,  # Hekkipekki
    771806222525267968,  # Shadé
    251004817844076554,  # Magemil
    260495039686246400,  # Raitila
    321966396864987137,  # Rajensen
    369109810311987200,  # Maverinkel
    239532428073500672,  # Darkpreacha
    344496860855009280,  # Lenef
    710915046200574073,  # MistaProfessa
    248796420880990208,  # Turit
]