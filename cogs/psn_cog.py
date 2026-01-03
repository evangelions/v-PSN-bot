import base64
import io
import json
from datetime import datetime, timedelta
from urllib.request import urlopen


import discord
import pycountry
from colorthief import ColorThief
from discord.ext import commands
from psnawp_api.core.psnawp_exceptions import PSNAWPForbidden
from psnawp_api.models.trophies.trophy_summary import TrophySummary

import config
from modules.custom_bot import Bot
from modules.date_formatter import translate_date


class Field:
    def __init__(self, name, value, inline=True):
        self.name = name
        self.value = value
        self.inline = inline


class Trophy:
    def __init__(self, trophy_infos: TrophySummary, user_id: int, bot):
        self.trophy_infos = trophy_infos
        self.user_id = user_id
        self.bot = bot
        self.trophy_fields = self.format_trophies()

    def format_trophies(self):
        trophy_amounts = {
            self.bot.get_text(self.user_id, "bronze"): self.trophy_infos.earned_trophies.bronze,
            self.bot.get_text(self.user_id, "silver"): self.trophy_infos.earned_trophies.silver,
            self.bot.get_text(self.user_id, "gold"): self.trophy_infos.earned_trophies.gold,
            self.bot.get_text(self.user_id, "platinum"): self.trophy_infos.earned_trophies.platinum,
        }

        trophy_fields = []
        for trophy_name, trophy_amount in trophy_amounts.items():
            trophy_fields.append(Field(trophy_name, f"`{trophy_amount}`"))

        trophy_fields.extend(
            [
                Field(
                    self.bot.get_text(self.user_id, "level_progress"),
                    f"`{self.trophy_infos.trophy_level}` | `{self.trophy_infos.progress}%`",
                ),
                Field(
                    self.bot.get_text(self.user_id, "total"),
                    f"`{sum(trophy_amounts.values())}`",
                ),
            ]
        )

        return trophy_fields


class PSNCog(commands.Cog):

    def __init__(self, bot):
        self.bot: Bot = bot

    @discord.slash_command(
        name="user-search",
        description="Display information concerning the given PSN account by using its name or id",
    )
    @discord.option(
        name="private",
        description="Should the message revealing your account details be private or public",
    )
    @discord.option(name="online_id", description="The GamerTag of the user.")
    @discord.option(name="account_id", description="The id of the user's account.")
    async def account_info(
        self,
        ctx: discord.ApplicationContext,
        online_id: str = None,
        account_id: str = None,
        private: bool = False,
    ):
        await ctx.response.defer(ephemeral=private)

        await self.register_usage(ctx.author.id)

        if account_id and online_id:
            raise ValueError(self.bot.get_text(ctx.author.id, "psn_user_argument_conflict"))
        elif online_id is None and account_id is None:
            raise ValueError(self.bot.get_text(ctx.author.id, "psn_missing_argument"))
        elif online_id is not None:
            user = self.bot.psnawp.user(online_id=online_id)
            account_id = user.account_id
        elif account_id is not None:
            user = self.bot.psnawp.user(account_id=account_id)

        user_profile = user.profile()
        user_friendship = user.friendship()
        user_language: list[str] = user_profile["languages"]
        user_region = user_language[0].split("-")[1]
        user_avatar = user_profile["avatars"][1]["url"]

        try:
            user_avatar_primary_color = await self.get_url_primary_color(user_avatar)
        except Exception:
            user_avatar_primary_color = discord.Color.blue()

        embed = discord.Embed(
            title=self.bot.get_text(ctx.author.id, "psn_user_title"),
            color=user_avatar_primary_color,
            timestamp=datetime.now(),
        )

        embed.set_author(
            name=self.bot.get_text(ctx.author.id, "psn_user_account"),
            icon_url=config.PSN_ACCOUNT_ICON_URL,
        )

        embed.set_thumbnail(url=user_avatar)

        image_url = f"https://image.api.playstation.com/profile/images/acct/prod/{account_id}/profile.JPEG?img="
        embed.set_image(url=image_url)

        footer_text = self.bot.get_text(
            ctx.author.id,
            "psn_user_viewcount",
            exec_amount=self.bot.users_json[str(ctx.author.id)],
        )
        embed.set_footer(
            text=f"{footer_text} | {self.bot.get_text(ctx.author.id, 'host')}"
        )

        fields = self.set_embed_fields(
            ctx.author,
            user,
            user_profile,
            user_friendship,
            user_region,
        )

        for field in fields:
            embed.add_field(name=field.name, value=field.value, inline=field.inline)

        await ctx.followup.send(f"{ctx.user.mention}", embed=embed, ephemeral=private)
        print(f"Obtained data for: {user.online_id}")

    async def register_usage(self, user_id: int):
        user_id = str(user_id)
        if self.bot.users_json.get(user_id) is not None:
            self.bot.users_json[user_id] += 1
        else:
            self.bot.users_json[user_id] = 1

        with open(config.CACHE_USERS, "w") as json_file:
            json.dump(self.bot.users_json, json_file)

    async def get_url_primary_color(self, url: str) -> discord.Color:
        fd = urlopen(url)
        image = io.BytesIO(fd.read())
        color_thief = ColorThief(image)
        primary_color = color_thief.get_color(quality=15)
        return discord.Color.from_rgb(r=primary_color[0], g=primary_color[1], b=primary_color[2])

    def set_embed_fields(
        self,
        author,
        user,
        user_profile,
        user_friendship,
        user_region,
    ) -> list[Field]:
        user_id = author.id
        fields = []

        # 1. Online ID (first)
        fields.append(
            Field(self.bot.get_text(user_id, "online_id"), f"`{user.online_id}`")
        )

        # 2. Region (directly below Online ID)
        try:
            region_field = Field(
                self.bot.get_text(user_id, "region_flag", flag=f":flag_{user_region.lower()}:"),
                f"`{user_region}` | `{pycountry.countries.get(alpha_2=user_region).name}`",
            )
        except AttributeError:
            region_field = Field(
                self.bot.get_text(user_id, "region_unknown"),
                f"`{self.bot.get_text(user_id, 'private')}`",
            )
        fields.append(region_field)

        # Rest of the fields (unchanged order)
        fields.extend([
            Field(
                self.bot.get_text(user_id, "ps_plus"),
                f"{'`✅`' if user_profile['isPlus'] else '`❌`'}",
            ),
            Field(
                self.bot.get_text(user_id, "officially_verified"),
                f"{'`✅`' if user_profile['isOfficiallyVerified'] else '`❌`'}",
            ),
            Field(self.bot.get_text(user_id, "account_id"), f"`{user.account_id}`"),
            Field(
                self.bot.get_text(user_id, "hex"),
                f"`{(f'{int(user.account_id):016x}'.upper())}`",
            ),
            Field(
                self.bot.get_text(user_id, "base64"),
                f"`{base64.b64encode(int(user.account_id).to_bytes(8, 'little')).decode('ascii').upper()}`",
            ),
            Field(
                self.bot.get_text(user_id, "social"),
                f"{self.bot.get_text(user_id, 'friends')}: `{user_friendship['friendsCount'] if user_friendship['friendsCount'] >= 0 else self.bot.get_text(user_id, 'private')}`",
                False,
            ),
        ])

        self.get_trophy_info(author, user, fields)
        self.get_user_presence(author, user, fields)
        self.get_titles(author, user, fields)

        fields.append(
            Field(
                self.bot.get_text(user_id, "about_me"),
                f"```{user_profile['aboutMe'] if user_profile['aboutMe'] else self.bot.get_text(user_id, 'not_visible')}```",
                False,
            )
        )

        fields.append(
            Field(
                self.bot.get_text(user_id, "previous_online_id"),
                f"`{user.prev_online_id}`",
                False,
            ),
        )

        return fields

    def get_trophy_info(self, author, user, fields):
        user_id = author.id
        try:
            trophy_infos = user.trophy_summary()
            trophies = Trophy(trophy_infos, user_id, self.bot)
            fields.extend(trophies.trophy_fields)
        except PSNAWPForbidden:
            fields.append(
                Field(
                    self.bot.get_text(user_id, "trophies"),
                    f"`{self.bot.get_text(user_id, 'private')}`",
                )
            )

    def get_user_presence(self, author, user, fields):
        try:
            user_presence = user.get_presence()["basicPresence"]
            user_presence_info = user_presence["primaryPlatformInfo"]
            current_game = self.extract_current_game(user_presence)
            self.process_presence_status(author, user_presence, user_presence_info, current_game, fields)
        except PSNAWPForbidden:
            fields.append(
                Field(
                    self.bot.get_text(author.id, "user_presence"),
                    f"`{self.bot.get_text(author.id, 'private')}`",
                )
            )

    def extract_current_game(self, user_presence):
        current_game = user_presence.get("gameTitleInfoList")
        if current_game:
            return current_game[0]["titleName"]
        return None

    def process_presence_status(self, author, user_presence, user_presence_info, current_game, fields):
        if user_presence_info["onlineStatus"] == "offline":
            self.process_offline_status(author, user_presence_info, fields)
        else:
            self.process_online_status(author, user_presence, user_presence_info, current_game, fields)

    def process_offline_status(self, author, user_presence_info, fields):
        try:
            last_online = datetime.strptime(user_presence_info["lastOnlineDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
            presence_data = f"<t:{int(last_online.timestamp())}:R> {user_presence_info['platform'].upper()}"
        except KeyError:
            presence_data = self.bot.get_text(author.id, "console_absent")
        fields.append(Field(self.bot.get_text(author.id, "last_seen"), presence_data, False))

    def process_online_status(self, author, user_presence, user_presence_info, current_game, fields):
        presence_data = f"`{self.bot.get_text(author.id, 'currently_online')}` {user_presence_info['platform'].upper()}"
        fields.append(Field(self.bot.get_text(author.id, "last_seen"), presence_data, False))

        availability: str = user_presence["availability"]
        availability = availability.replace("unavailable", self.bot.get_text(author.id, "unavailable"))
        availability = availability.replace("availableToPlay", self.bot.get_text(author.id, "ready_to_play"))

        fields.append(Field(self.bot.get_text(author.id, "availability"), availability, False))

        if current_game:
            fields.append(Field(self.bot.get_text(author.id, "playing"), f"`{current_game}`", False))

    def get_titles(self, author, user, fields):
        user_id = author.id
        try:
            all_titles = user.title_stats()

            # Recent games
            recent_titles = []
            for i, title in enumerate(all_titles):
                if i == config.MAX_GAMES_DISPLAY:
                    break
                launched_text = self.bot.get_text(user_id, "launched", timestamp=int(title.last_played_date_time.timestamp()))
                played_times_text = self.bot.get_text(user_id, "played_times", play_count=title.play_count)
                played_duration_text = self.bot.get_text(user_id, "played_duration", play_duration=translate_date(str(title.play_duration), user_id, self.bot))

                recent_titles.append(f"{title.name}\n{launched_text}\n{played_times_text}\n{played_duration_text}")

            fields.append(Field(self.bot.get_text(user_id, "recent_games"), "\n\n".join(recent_titles)))

            # Favorite games & total stats
            total_playtime = timedelta(seconds=0)
            all_favorite_titles = []
            for title in all_titles:
                total_playtime += title.play_duration
                all_favorite_titles.append(title)

            total_games = len(all_favorite_titles)
            all_favorite_titles = sorted(all_favorite_titles, key=lambda x: x.play_duration, reverse=True)

            favorite_titles = []
            for i, title in enumerate(all_favorite_titles):
                if i == config.MAX_GAMES_DISPLAY:
                    break
                launched_text = self.bot.get_text(user_id, "launched", timestamp=int(title.last_played_date_time.timestamp()))
                played_times_text = self.bot.get_text(user_id, "played_times", play_count=title.play_count)
                played_duration_text = self.bot.get_text(user_id, "played_duration", play_duration=translate_date(str(title.play_duration), user_id, self.bot))

                favorite_titles.append(f"{title.name}\n{launched_text}\n{played_times_text}\n{played_duration_text}")

            fields.append(Field(self.bot.get_text(user_id, "favorite_games"), "\n\n".join(favorite_titles)))

            fields.append(Field(self.bot.get_text(user_id, "total_play_time"), f"`{translate_date(str(total_playtime), user_id, self.bot)}`", inline=False))
            fields.append(Field(self.bot.get_text(user_id, "total_games"), f"`{total_games}`"))
        except PSNAWPForbidden:
            fields.append(Field(self.bot.get_text(user_id, "games"), f"`{self.bot.get_text(user_id, 'private')}`"))

    @discord.slash_command(name="game-search", description="Allows you to look up a game on the Playstation Store.")
    @discord.option(name="game_name", description="The name of the game to look for.")
    @discord.option(name="search_index", description="The result index to return (depends on search results amounts).")
    async def search_game(self, ctx: discord.ApplicationContext, game_name: str, search_index: int = 0):
        await ctx.defer()
        # ... (game-search command unchanged, omitted for brevity)

    @discord.slash_command(name="list-recent-games", description="List all of the recently played games by the user.")
    async def list_recent_games(self, ctx: discord.ApplicationContext, online_id: str):
        await ctx.defer()
        # ... (list-recent-games command unchanged, omitted for brevity)


def setup(bot):
    bot.add_cog(PSNCog(bot))
