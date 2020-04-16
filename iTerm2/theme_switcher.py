#!/usr/bin/env python3

import asyncio
import iterm2

async def get_colour_preset(connection, theme):
    """Return the dark or light colour preset based on the given theme."""
    parts = theme.split(" ")
    if "dark" in parts:
        return await iterm2.ColorPreset.async_get(connection, "Solarized Dark")
    else:
        return await iterm2.ColorPreset.async_get(connection, "Solarized Light")

async def set_colour_preset(connection, preset):
    """Set the colour preset for all profiles."""
    profiles=await iterm2.PartialProfile.async_query(connection)
    for partial in profiles:
        profile = await partial.async_get_full_profile()
        await profile.async_set_color_preset(preset)

async def main(connection):
    """Set the correct colour preset based on the current theme."""
    app = await iterm2.async_get_app(connection)
    theme = await app.async_get_variable("effectiveTheme")
    preset = await get_colour_preset(connection, theme)
    await set_colour_preset(connection, preset)


iterm2.run_until_complete(main)
