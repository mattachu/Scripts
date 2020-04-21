#!/usr/bin/env python3

import asyncio
import iterm2
import theme_switcher

async def switch_on_theme_change(connection):
    """Continuously monitor the effective theme for changes."""
    async with iterm2.VariableMonitor(connection, iterm2.VariableScopes.APP, "effectiveTheme", None) as mon:
        while True:
            theme = await mon.async_get()
            is_dark = theme_switcher.is_dark_theme(theme)
            preset = await theme_switcher.get_colour_preset(connection, is_dark)
            ansi_8_color = theme_switcher.get_ansi_8_color(is_dark)
            await theme_switcher.set_colours(connection, preset, ansi_8_color)

if __name__ == '__main__':
    iterm2.run_forever(switch_on_theme_change)
