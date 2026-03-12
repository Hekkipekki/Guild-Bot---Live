from logic.embed.comp_embed import build_comp_embed


async def post_comp_message(channel, comp_data: dict) -> tuple[bool, str]:
    mentions = comp_data.get("mentions", [])
    mention_text = " ".join(mentions)

    embed = build_comp_embed(comp_data)

    if mention_text:
        await channel.send(mention_text)

    await channel.send(embed=embed)
    return True, "Comp message posted."