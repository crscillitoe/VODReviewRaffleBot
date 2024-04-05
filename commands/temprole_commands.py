from discord import (
    Colour,
    Embed,
    Role,
    app_commands,
    Interaction,
    Client,
    User,
    utils
)
from config import YAMLConfig as Config

from controllers.temprole_controller import TempRoleController
from util.discord_utils import DiscordUtils

MOD_ROLE = Config.CONFIG["Discord"]["Roles"]["Mod"]
#these are hardcoded until raze to radiant is over, or config file changes are allowed
#for testing on own setup, these need to be changed to your appropriate IDs
#CM_ROLE should be 1044433022537191515 when committing and refers to the Community Manager role
#TEMPROLE_AUDIT_CHANNEL should be 1225769539267199026 when committing and refers to the temprole-logs channel
CM_ROLE = 1044433022537191515
TEMPROLE_AUDIT_CHANNEL = 1225769539267199026
COLOR_FAIL = Colour.red()

@app_commands.guild_only()
class TemproleCommands(app_commands.Group, name="temprole"):
    def __init__(self, tree: app_commands.CommandTree, client: Client) -> None:
        super().__init__()
        self.tree = tree
        self.client = client

    @app_commands.command(name="set")
    @app_commands.checks.has_any_role(MOD_ROLE, CM_ROLE)
    @app_commands.describe(user="Discord User to assign role to")
    @app_commands.describe(role="Discord Role to assign role to")
    @app_commands.describe(duration="Duration of temprole")
    async def set_role(
        self, interaction: Interaction, user: User, role: Role, duration: str
    ):
        """Assign temprole to a user for a specified time (10m, 30d, 3w, etc)"""
        audit_channel = interaction.guild.get_channel(TEMPROLE_AUDIT_CHANNEL)
        authorised, message = await TempRoleController.authorise_role_usage(role)
        color = Colour.green()
        audit_failed_message = f"Tried to assign {role.name} to {user.mention} \n System returned message: \n"

        if not authorised:
            await DiscordUtils.audit(interaction, audit_failed_message + message, audit_channel, COLOR_FAIL)
            return await DiscordUtils.reply(
                interaction, content=message, ephemeral=True
            )

        success, message = await TempRoleController.set_role(user, role, duration)

        if not success:
            await DiscordUtils.audit(interaction, audit_failed_message + message, audit_channel, COLOR_FAIL)
            return await DiscordUtils.reply(
                interaction, content=message, ephemeral=True
            )

        embed = Embed(
            title="Assigned Temprole",
            description=message,
            color=color,
        )
        await DiscordUtils.reply(interaction, embed=embed)

        await DiscordUtils.audit(interaction,message,audit_channel,color)

    @app_commands.command(name="extend")
    @app_commands.checks.has_any_role(MOD_ROLE, CM_ROLE)
    @app_commands.describe(user="Discord User to extend role for")
    @app_commands.describe(role="Discord Role to extend duration for")
    @app_commands.describe(duration="Duration to add to temprole")
    async def extend_role(
        self, interaction: Interaction, user: User, role: Role, duration: str
    ):
        """Assign temprole to a user for a specified time (10m, 30d, 3w, etc)"""
        audit_channel = interaction.guild.get_channel(TEMPROLE_AUDIT_CHANNEL)
        authorised, message = await TempRoleController.authorise_role_usage(role)
        color = Colour.green()
        audit_failed_message = f"Tried to extend {role.name} on {user.mention} \n System returned message: \n"

        if not authorised:
            await DiscordUtils.audit(interaction, audit_failed_message + message, audit_channel, COLOR_FAIL)
            return await DiscordUtils.reply(
                interaction, content=message, ephemeral=True
            )

        success, message = await TempRoleController.extend_role(user, role, duration)

        if not success:
            await DiscordUtils.audit(interaction, audit_failed_message + message, audit_channel, COLOR_FAIL)
            return await DiscordUtils.reply(
                interaction, content=message, ephemeral=True
            )

        embed = Embed(
            title="Assigned Temprole",
            description=message,
            color=color,
        )
        await DiscordUtils.reply(interaction, embed=embed)

        await DiscordUtils.audit(interaction,message,audit_channel,color)

    @app_commands.command(name="remove")
    @app_commands.checks.has_any_role(MOD_ROLE, CM_ROLE)
    @app_commands.describe(user="Discord User to remove role from")
    @app_commands.describe(role="Discord Role to remove")
    async def remove_role(self, interaction: Interaction, user: User, role: Role):
        """Assign temprole to a user for a specified time (10m, 30d, 3w, etc)"""
        audit_channel = interaction.guild.get_channel(TEMPROLE_AUDIT_CHANNEL)
        authorised, message = await TempRoleController.authorise_role_usage(role)
        color = Colour.red()
        audit_failed_message = f"Tried to remove {role.name} from {user.mention} \n System returned message: \n"

        if not authorised:
            await DiscordUtils.audit(interaction, audit_failed_message + message, audit_channel, COLOR_FAIL)
            return await DiscordUtils.reply(
                interaction, content=message, ephemeral=True
            )

        success, message = await TempRoleController.remove_role(user, role)

        if not success:
            await DiscordUtils.audit(interaction, audit_failed_message + message, audit_channel, COLOR_FAIL)
            return await DiscordUtils.reply(
                interaction, content=message, ephemeral=True
            )

        embed = Embed(
            title="Removed Temprole",
            description=message,
            color=color,
        )
        await DiscordUtils.reply(interaction, embed=embed)

        await DiscordUtils.audit(interaction,message,audit_channel,color)

    @app_commands.command(name="status")
    @app_commands.checks.has_any_role(MOD_ROLE, CM_ROLE)
    @app_commands.describe(user="Discord User to check roles for")
    async def status(self, interaction: Interaction, user: User):
        """See expirations for all temproles currently assigned to given user"""
        await TempRoleController.view_temproles(user, interaction)

    @app_commands.command(name="mine")
    async def mine(self, interaction: Interaction):
        """See expirations for all temproles currently assigned to you"""
        await TempRoleController.view_temproles(interaction.user, interaction)

    @app_commands.command(name="view")
    @app_commands.checks.has_any_role(MOD_ROLE, CM_ROLE)
    @app_commands.describe(role="Discord Role to check users for")
    async def view(self, interaction: Interaction, role: Role):
        """See expirations for all users that currently have a given role"""
        audit_channel = interaction.guild.get_channel(TEMPROLE_AUDIT_CHANNEL)
        authorised, message = await TempRoleController.authorise_role_usage(role)
        audit_failed_message = f"Tried to view duration of {role.name} on {user.mention} \n System returned message: \n"

        if not authorised:
            await DiscordUtils.audit(interaction, audit_failed_message + message, audit_channel, COLOR_FAIL)
            return await DiscordUtils.reply(
                interaction, content=message, ephemeral=True
            )

        await TempRoleController.view_users(role, interaction)
