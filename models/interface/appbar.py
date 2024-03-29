import asyncio
import os
import subprocess
import sys
from pathlib import Path

from aiohttp import ClientSession
from flet import (
    AppBar,
    IconButton,
    PopupMenuButton,
    PopupMenuItem,
    Divider,
    Column,
    Row,
    Text,
    Container,
    Image,
    AlertDialog,
    TextButton,
    MainAxisAlignment,
    Icon,
    Theme,
    ButtonStyle,
    TextField,
)
from datetime import datetime
from flet_core.colors import SURFACE_VARIANT
from flet_core.icons import (
    LIGHT_MODE,
    DARK_MODE,
    LANGUAGE,
    BUG_REPORT,
    HELP,
    DOWNLOAD,
    PALETTE,
    SAVINGS,
    PERSON,
    FEEDBACK,
    PEST_CONTROL,
    HISTORY_EDU,
)

from models.preferences import AccentColor
from utils.functions import check_update
from utils.localization import Locale
from utils.tasks import loop


async def check_update(current_version, debug=False, force=False):
    async with ClientSession() as session:
        async with session.get(
            "https://api.github.com/repos/Sly0511/RenewedTroveTools/releases"
        ) as response:
            version_data = await response.json()
            try:
                version = version_data[0]
            except IndexError:
                return None
            if current_version != version.get("name") or force:
                if os.name == "nt":
                    for asset in version.get("assets"):
                        if "debug" not in asset.get("name") and not debug:
                            return asset.get("browser_download_url"), os.name == "nt"
                        elif "debug" in asset.get("name") and debug:
                            return asset.get("browser_download_url"), os.name == "nt"
                else:
                    return version.get("html_url"), os.name == "nt"
    return None, os.name == "nt"


class CustomAppBar(AppBar):
    def __init__(self, page, **kwargs):
        self.page = page
        actions = self.build_actions(kwargs)
        super().__init__(
            bgcolor=SURFACE_VARIANT,
            actions=actions,
            center_title=True,
            **kwargs,
        )
        self.i = 0
        if not page.web:
            self.check_updates.start()

    @loop(seconds=120)
    async def check_updates(self):
        await self.check_for_update()

    def build_actions(self, kwargs):
        actions = []
        actions.extend(
            [
                IconButton(
                    icon=DOWNLOAD,
                    on_click=self.go_to_update_page,
                    visible=False,
                    tooltip="A newer version is available.",
                ),
                IconButton(
                    icon=HISTORY_EDU,
                    on_click=self.display_changelog,
                    tooltip="Changelog",
                ),
                IconButton(
                    icon=FEEDBACK,
                    on_click=self.feedback_modal,
                    tooltip="Send feedback",
                ),
                IconButton(
                    data="theme_switcher",
                    icon=DARK_MODE if self.page.dark_theme else LIGHT_MODE,
                    on_click=self.change_theme,
                    tooltip="Change theme",
                ),
                PopupMenuButton(
                    icon=PALETTE,
                    items=[
                        PopupMenuItem(
                            data=color,
                            content=Row(
                                controls=[
                                    Icon(PALETTE, color=color.value),
                                    Text(
                                        value=" ".join(
                                            [
                                                w.capitalize()
                                                for w in color.value.split("_")
                                            ]
                                        )
                                    ),
                                ]
                            ),
                            on_click=self.change_color,
                        )
                        for color in AccentColor
                    ],
                ),
                PopupMenuButton(
                    content=Container(
                        Row(
                            controls=[
                                Icon(LANGUAGE),
                                # Text(
                                #     self.page.app_config.locale.name.replace("_", " ")
                                # ),
                            ]
                        )
                    ),
                    items=[
                        PopupMenuItem(
                            data=loc,
                            text=loc.name.replace("_", " "),
                            on_click=self.change_locale,
                        )
                        for loc in Locale
                    ],
                    visible=False,
                    tooltip="Change language (Broken)",
                ),
                PopupMenuButton(
                    data="donate-buttons",
                    icon=SAVINGS,
                    tooltip="Donate",
                    items=[
                        PopupMenuItem(
                            data="paypal",
                            content=Row(
                                controls=[
                                    Image(
                                        "assets/icons/brands/paypal-mark.png", width=19
                                    ),
                                    Text("Paypal"),
                                ]
                            ),
                            on_click=self.go_url,
                        ),
                        PopupMenuItem(
                            data="kofi",
                            content=Row(
                                controls=[
                                    Image(
                                        "assets/icons/brands/kofi-mark.png", width=24
                                    ),
                                    Text("Kofi"),
                                ]
                            ),
                            on_click=self.go_url,
                        ),
                    ],
                ),
                *(
                    [
                        PopupMenuButton(
                            data="user-buttons",
                            content=Row(
                                controls=(
                                    [
                                        Image(
                                            self.page.user_data["avatar_url"],
                                            error_content=Icon(PERSON),
                                            width=40,
                                            border_radius=50,
                                        ),
                                        Text(self.page.user_data["username"]),
                                    ]
                                    if self.page.user_data is not None
                                    else [
                                        TextButton(
                                            icon=PERSON,
                                            text="Login",
                                            style=ButtonStyle(color="secondary"),
                                            on_click=self.page.RTT.display_login_screen,
                                        )
                                    ]
                                )
                            ),
                            items=(
                                [
                                    PopupMenuItem(
                                        data="logout",
                                        text="Logout",
                                        on_click=self.page.RTT.execute_logout,
                                    ),
                                ]
                                if self.page.user_data is not None
                                else []
                            ),
                        ),
                    ]
                    if not self.page.web
                    else []
                ),
                PopupMenuButton(
                    data="other-buttons",
                    items=[
                        PopupMenuItem(
                            data="discord",
                            content=Row(
                                controls=[
                                    Image(
                                        (
                                            "assets/icons/brands/discord-mark-black.png"
                                            if not self.page.dark_theme
                                            else "assets/icons/brands/discord-mark-white.png"
                                        ),
                                        width=19,
                                    ),
                                    Text("Discord"),
                                ]
                            ),
                            on_click=self.go_url,
                        ),
                        PopupMenuItem(
                            data="github",
                            content=Row(
                                controls=[
                                    Image(
                                        (
                                            "assets/icons/brands/github-mark-black.png"
                                            if not self.page.dark_theme
                                            else "assets/icons/brands/github-mark-white.png"
                                        ),
                                        width=19,
                                    ),
                                    Text("Github"),
                                ]
                            ),
                            on_click=self.go_url,
                        ),
                        Divider(),
                        PopupMenuItem(
                            icon=BUG_REPORT,
                            data="discord",
                            text="Report a bug",
                            on_click=self.go_url,
                        ),
                        *(
                            [
                                PopupMenuItem(
                                    icon=PEST_CONTROL,
                                    text=(
                                        "Switch to debug version"
                                        if not self.page.metadata.dev
                                        else "Switch to release version"
                                    ),
                                    on_click=self.switch_debug,
                                )
                            ]
                            if not self.page.web
                            else []
                        ),
                        PopupMenuItem(
                            icon=HELP, text="About", on_click=self.open_about
                        ),
                    ],
                    tooltip="Others",
                ),
            ]
        )
        actions.extend(kwargs.get("actions", []))
        return actions

    async def change_theme(self, _):
        self.page.theme_mode = "LIGHT" if not self.page.dark_theme else "DARK"
        await self.page.client_storage.set_async("theme", self.page.theme_mode)
        for action in self.actions:
            if action.data == "theme_switcher":
                action.icon = (
                    DARK_MODE if self.page.theme_mode == "LIGHT" else LIGHT_MODE
                )
            if action.data == "other-buttons":
                for item in action.items:
                    if item.data in ["discord", "github"] and item.content is not None:
                        item.content.controls[0].src = (
                            f"assets/icons/brands/{item.data}-mark-black.png"
                            if self.page.theme_mode == "LIGHT"
                            else f"assets/icons/brands/{item.data}-mark-white.png"
                        )

        await self.page.update_async()

    async def display_changelog(self, event):
        content = Column(expand=True, scroll=True)
        async with ClientSession() as session:
            async with session.get(
                "https://kiwiapi.slynx.xyz/v1/misc/change_log"
            ) as response:
                data = await response.json()
                for version, version_data in sorted(
                    data.items(),
                    key=lambda x: -datetime.fromisoformat(x[1]["time"]).timestamp(),
                ):
                    content.controls.append(
                        Column(
                            controls=[
                                Text(
                                    f"Version {version}",
                                    size=20,
                                ),
                                *(
                                    [
                                        Text(
                                            " " * 5
                                            + f"{change['author']} - {change['message']}",
                                            size=15,
                                        )
                                        for change in version_data["commits"]
                                    ]
                                ),
                            ],
                        )
                    )
        self.dlg = AlertDialog(
            modal=True,
            title=Text("Changelog"),
            actions=[
                TextButton("Close", on_click=self.close_dlg),
            ],
            actions_alignment=MainAxisAlignment.END,
            content=content,
        )
        self.page.dialog = self.dlg
        self.dlg.open = True
        await self.page.update_async()

    async def check_for_update(self):
        await asyncio.sleep(1)
        if (await check_update(self.page.metadata.version, self.page.metadata.dev))[
            0
        ] is not None:
            self.page.appbar.actions[0].visible = True
            self.page.snack_bar.content.value = "A new update is available"
            self.page.snack_bar.bgcolor = "yellow"
            self.page.snack_bar.open = True
            self.page.snack_bar.duration = 1000
            await self.page.snack_bar.update_async()
            await self.page.appbar.update_async()

    async def feedback_modal(self, event):
        self.feedback_text = TextField(
            width=800,
            expand=True,
            multiline=True,
            max_lines=10,
            min_lines=5,
        )
        self.dlg = AlertDialog(
            modal=True,
            title=Text("Feedback"),
            actions=[
                TextButton("Close", on_click=self.close_dlg),
                TextButton("Send", on_click=self.send_feedback),
            ],
            actions_alignment=MainAxisAlignment.END,
            content=self.feedback_text,
        )
        self.page.dialog = self.dlg
        self.dlg.open = True
        await self.page.update_async()

    async def send_feedback(self, event):
        async with ClientSession() as session:
            data = {
                "message": self.feedback_text.value,
            }
            await session.post(
                "https://kiwiapi.slynx.xyz/v1/misc/feedback",
                json=data,
            )
        self.dlg.open = False
        await self.page.update_async()

    async def switch_debug(self, event):
        await self.go_to_update_page(event, True)

    async def go_to_update_page(self, event, invert=False):
        dev = self.page.metadata.dev
        if invert:
            dev = not dev
        update_url, is_windows = await check_update(
            self.page.metadata.version, dev, True
        )
        if is_windows:
            self.page.controls = [
                Column(
                    controls=[
                        Text(
                            "Downloading update, please wait...",
                            text_align="center",
                            size=40,
                        )
                    ],
                    alignment="center",
                    horizontal_alignment="center",
                    expand=True,
                ),
            ]
            event.control.disabled = True
            await self.page.update_async()
            async with ClientSession() as session:
                async with session.get(update_url) as response:
                    if response.status == 200:
                        exe_path = Path(sys.executable)
                        exe_location = exe_path.parent
                        appdata = Path(os.getenv("APPDATA"))
                        rtt_path = appdata.joinpath("Trove/sly.dev").joinpath(
                            self.page.metadata.tech_name
                        )
                        update_file = rtt_path / "update.msi"
                        update_file.write_bytes(await response.read())
                        subprocess.Popen(
                            [
                                "update.bat",
                                str(exe_location),
                                str(update_file),
                            ],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                        )
                        await self.page.window_close_async()
        else:
            await self.page.launch_url_async(update_url)

    async def change_theme(self, _):
        self.page.theme_mode = "light" if self.page.theme_mode == "dark" else "dark"
        for action in self.actions:
            if action.data == "theme_switcher":
                action.icon = (
                    DARK_MODE if self.page.theme_mode == "light" else LIGHT_MODE
                )
            if action.data == "other-buttons":
                for item in action.items:
                    if item.data in ["discord", "github"] and item.content is not None:
                        item.content.controls[0].src = (
                            f"assets/icons/brands/{item.data}-mark-black.png"
                            if self.page.theme_mode == "light"
                            else f"assets/icons/brands/{item.data}-mark-white.png"
                        )
        self.page.preferences.theme = self.page.theme_mode
        self.page.preferences.save()
        await self.page.update_async()

    async def change_locale(self, event):
        self.page.constants.app_config.locale = event.control.data
        await self.page.client_storage.set_async("locale", event.control.data.value)
        await self.page.restart(True)

    async def update_appbar(self):
        self.actions = self.build_actions(dict())
        await self.update_async()

    async def go_url(self, event):
        urls = {
            "discord": "https://discord.gg/MbByECEc5k",
            "github": "https://github.com/Sly0511/RenewedTroveTools",
            "paypal": "https://www.paypal.com/paypalme/waterin",
            "kofi": "https://ko-fi.com/slydev",
        }
        await self.page.launch_url_async(urls[event.control.data])

    async def open_about(self, event):
        self.dlg = AlertDialog(
            modal=True,
            title=Text("About"),
            actions=[
                TextButton("Close", on_click=self.close_dlg),
            ],
            actions_alignment=MainAxisAlignment.END,
            content=Text(
                "This application was developed by Sly. Interface design improved by Cr0nicl3 D3str0y3r.\n\nI am coding this as an hobby with the goal of"
                " achieving greater front-end building skills, at the same time I also improve code"
                " making and organization skills\n\nI have the goal to not only build something"
                " that is usable but mostly updatable with little effort or code knowledge"
                " this however may be a challenge if newer updates come with changes on behavior of"
                " previous content.\n\nI don't promise to keep this up to date forever, but as long as"
                " I am around I should be able to.\n\nThanks for using my application. <3"
            ),
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = self.dlg
        self.dlg.open = True
        await self.page.update_async()

    async def close_dlg(self, e):
        self.dlg.open = False
        await self.page.update_async()

    async def change_color(self, event):
        color = event.control.data
        self.page.theme = Theme(color_scheme_seed=color)
        self.page.preferences.accent_color = color
        self.page.preferences.save()
        await self.page.update_async()
