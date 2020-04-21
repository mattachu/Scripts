#!/usr/bin/env python3

import asyncio
import iterm2

def is_dark_theme(theme):
    """Work out whether a theme is dark or not."""
    parts = theme.split(" ")
    if "dark" in parts:
        return True
    else:
        return False

def get_ansi_8_color(is_dark):
    """Return a colour for ANSI 8 to match the dark or light colour preset."""
    if is_dark:
        return iterm2.Color(59, 109, 124)
    else:
        return iterm2.Color(114, 114, 124)

async def get_colour_preset(connection, is_dark):
    """Return the dark or light colour preset."""
    if is_dark:
        return await iterm2.ColorPreset.async_get(connection, "Solarized Dark")
    else:
        return await iterm2.ColorPreset.async_get(connection, "Solarized Light")

async def set_colours(connection, preset, ansi_8_color):
    """Set the colour preset for all profiles."""
    profiles = await iterm2.PartialProfile.async_query(connection)
    for partial in profiles:
        profile = await partial.async_get_full_profile()
        await profile.async_set_color_preset(preset)
        await profile.async_set_ansi_8_color(ansi_8_color)

async def main(connection):
    """Continuously monitor the effective theme for changes."""
    async with iterm2.VariableMonitor(connection, iterm2.VariableScopes.APP, "effectiveTheme", None) as mon:
        while True:
            theme = await mon.async_get()
            is_dark = is_dark_theme(theme)
            preset = await get_colour_preset(connection, is_dark)
            ansi_8_color = get_ansi_8_color(is_dark)
            await set_colours(connection, preset, ansi_8_color)

iterm2.run_forever(main)
