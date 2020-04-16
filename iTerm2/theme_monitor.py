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
    """Continuously monitor the effective theme for changes."""
    async with iterm2.VariableMonitor(connection, iterm2.VariableScopes.APP, "effectiveTheme", None) as mon:
        while True:
            theme = await mon.async_get()
            preset = await get_colour_preset(connection, theme)
            await set_colour_preset(connection, preset)

iterm2.run_forever(main)
