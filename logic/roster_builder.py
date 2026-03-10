import config

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