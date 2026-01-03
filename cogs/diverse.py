import discord
from discord.ext import commands

from modules.custom_bot import Bot
import json
import config


class Diverse(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @discord.slash_command(
        name="bot-infos", description="Gives utilitary informations about the bot."
    )
    async def get_bot_infos(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title=f"{self.bot.get_text(ctx.author.id, 'bot_infos_title')}",
            description=f"{self.bot.get_text(ctx.author.id, 'bot_infos_desc')}",
        )
        embed.add_field(
            name="Ping",
            value=f"{int(self.bot.latency * 1000)}ms",
            inline=False,
        )

        guilds = []
        for guild in self.bot.guilds:
            if config.ALLOW_SERVER_INVITES:
                try:
                    guild_invite = (
                        f"https://discord.gg/{(await guild.invites())[0].code}"
                    )
                    guild_name = f"[{guild.name}](https://discord.gg/{guild_invite})"
                except Exception:
                    guild_name = guild.name
            else:
                guild_name = guild.name

            guilds.append(
                f"- {guild_name} ({guild.member_count} {self.bot.get_text(ctx.author.id, 'members')})\n{self.bot.get_text(ctx.author.id, 'owned_by')}: {guild.owner.global_name}"
            )
        embed.add_field(
            name=f"{self.bot.get_text(ctx.author.id, 'servers')}",
            value="\n".join(guilds),
            inline=False,
        )
        embed.add_field(
            name=f"{self.bot.get_text(ctx.author.id, 'credits')}",
            value="- [PSNAWP API](https://pypi.org/project/psnawp-api/)\n- [IGDB](https://www.igdb.com/)",
            inline=False,
        )
        embed.set_footer(text=self.bot.get_text(ctx.author.id, "host"))

        await ctx.respond(embed=embed)

    @discord.slash_command(
        name="toggle-ban", description="Block/Unblock a user from using commands."
    )
    @commands.is_owner()
    async def toggle_ban(
        self,
        ctx: discord.ApplicationContext,
        member: discord.User,
        private: bool = False,
    ):
        await ctx.defer(ephemeral=private)

        if member.id == self.bot.owner_id:
            error_message = self.bot.get_text(
                ctx.author.id, "toggle_ban_cannot_ban_owner"
            )
            raise discord.ApplicationCommandError(error_message)

        if str(member.id) in self.bot.banned_user:
            self.bot.banned_user.remove(str(member.id))
            with open(config.BANNED_USERS, "w") as f:
                json.dump(self.bot.banned_user, f)

            response_message = self.bot.get_text(
                ctx.author.id, "toggle_ban_unbanned", member=member.name
            )
            await ctx.respond(response_message)
            print(f"{member.global_name} ({member.id}) was successfully unbanned.")
            return

        self.bot.banned_user.append(str(member.id))
        with open(config.BANNED_USERS, "w") as f:
            json.dump(self.bot.banned_user, f)

        response_message = self.bot.get_text(
            ctx.author.id, "toggle_ban_banned", member=member.name
        )
        await ctx.respond(response_message)
        print(f"{member.global_name} ({member.id}) was successfully banned.")

    @discord.slash_command(
        name="refresh-psn-token", description="Changes the NPSSO token to a new one."
    )
    @commands.is_owner()
    async def refresh_token(self, ctx: discord.ApplicationContext):
        self.bot.psnawp._request_builder.authenticator.obtain_fresh_access_token()
        response_message = self.bot.get_text(ctx.author.id, "refresh_token_success")
        await ctx.respond(response_message)
        print("Generated a new NPSSO token.")

def setup(bot):
    bot.add_cog(Diverse(bot))
