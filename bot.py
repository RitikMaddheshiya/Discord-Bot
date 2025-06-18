import discord
from discord.ext import commands
from discord import app_commands
import json
import os

TOKEN = bot token  # Replace with your bot token
GUILD_ID = 1382792314270781460  # Replace with your server's actual ID
DATA_FILE = 'message_counts.json'

MILESTONES = {
    10:   ("🎉 {user}, congratulations! You hit 10 messages! 🚀", None),
    30:   ("🥳 {user}, 30 messages! Keep it up, chatterbox! 💬", None),
    50:   ("🔥 {user}, 50 messages! You're on fire! 🔥", None),
    100:  ("💯 {user}, 100 messages! Century club! 🏅", None),
    150:  ("🌟 {user}, 150 messages! Shining bright! ✨", None),
    200:  ("🚀 {user}, 200 messages! Sky's the limit! 🌌", None),
    300:  ("🏆 {user}, 300 messages! Triple threat! 🥉", None),
    500:  ("🎊 {user}, 500 messages! Halfway to greatness! 🏆", None),
    800:  ("🎯 {user}, 800 messages! Almost at the big one! 🏁", None),
    1000: ("🥇 {user}, 1000 messages! Welcome, @yapper! 🗣️", "yapper"),
    2000: ("🌈 {user}, 2000 messages! Double trouble! 😎", None),
    3000: ("🚨 {user}, 3000 messages! You're unstoppable! 🚨", None),
    4000: ("👑 {user}, 4000 messages! You rule the chat! 👑", None),
    5000: ("🦈 {user}, 5000 messages! You are now a @yapper shark! 🦈", "yapper shark"),
    6000: ("💬 {user}, 6000 messages! Nonstop talking! 📣", None),
    7000: ("🌟 {user}, 7000 messages! Superstar chatter! ⭐", None),
    8000: ("🚀 {user}, 8000 messages! To infinity and beyond! 🛰️", None),
    9000: ("🔥 {user}, 9000 messages! Blazing the trail! 🔥", None),
    10000: ("🏆✨ {user}, 10,000 messages! You've entered the Hall of Yappers! 🌟🎇", "protentional yapper"),
    20000: ("🚀🌠 {user}, 20k messages! Cosmic Chatter achieved! 🌌👽", "space yapper"),
    30000: ("🎪🎤 {user}, 30k messages! Carnival of Conversation! 🎡🤹", None),
    40000: ("🏰⚔️ {user}, 40k messages! Castle of Chat conquered! 🛡️🗡️", "chat knight"),
    50000: ("🌋🔥 {user}, 50k messages! Eruption of Eloquence! 🧨💥", "volcano yapper"),
    60000: ("🧠💡 {user}, 60k messages! Genius Gabber unlocked! 📚🔍", "chat scholar"),
    70000: ("🌌🛸 {user}, 70k messages! Interstellar Yapping! 👾🚨", "alien yapper"),
    80000: ("🏅🎖️ {user}, 80k messages! Olympic-level Chatting! ⚽🏈", "chat athlete"),
    90000: ("👑💎 {user}, 90k messages! Crown Jewel of Conversation! 💍💰", "royal yapper"),
    100000: ("🌟🏆 {user}, 100K MESSAGES! YAPPER SUPREME! 🚀🎇\nYou've reached LEGENDARY status! 🏰⚔️", "yapper supreme")
}

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        message_counts = json.load(f)
else:
    message_counts = {}

def save_counts():
    with open(DATA_FILE, 'w') as f:
        json.dump(message_counts, f)

def get_user_count(guild_id, user_id):
    return message_counts.get(str(guild_id), {}).get(str(user_id), 0)

def set_user_count(guild_id, user_id, new_count):
    guild_id = str(guild_id)
    user_id = str(user_id)
    if guild_id not in message_counts:
        message_counts[guild_id] = {}
    message_counts[guild_id][user_id] = max(0, new_count)
    save_counts()
    return message_counts[guild_id][user_id]

def add_user_count(guild_id, user_id, amount):
    current = get_user_count(guild_id, user_id)
    return set_user_count(guild_id, user_id, current + amount)

def remove_user_count(guild_id, user_id, amount):
    current = get_user_count(guild_id, user_id)
    return set_user_count(guild_id, user_id, current - amount)

async def check_milestone(message, count):
    for milestone, (msg, role_name) in MILESTONES.items():
        if count == milestone:
            out_msg = msg.replace("{user}", message.author.mention)
            if role_name:
                role = discord.utils.get(message.guild.roles, name=role_name)
                if role:
                    await message.author.add_roles(role)
                    out_msg = out_msg.replace(f"@{role_name}", role.mention)
            await message.channel.send(out_msg)
            break

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    guild_id = str(message.guild.id)
    user_id = str(message.author.id)
    if guild_id not in message_counts:
        message_counts[guild_id] = {}
    if user_id not in message_counts[guild_id]:
        message_counts[guild_id][user_id] = 0

    message_counts[guild_id][user_id] += 1
    save_counts()

    await check_milestone(message, message_counts[guild_id][user_id])
    await bot.process_commands(message)

# /message_count command: anyone can check any user's count, pretty embed
@tree.command(name="message_count", description="See a user's message count", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="User to check (leave blank for yourself)")
async def message_count(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user
    count = get_user_count(interaction.guild.id, user.id)
    embed = discord.Embed(
        title="Message Count",
        description=f"{user.mention} has sent **{count}** messages!",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# /message_leaderboard: public, creative embed with avatars
@tree.command(name="message_leaderboard", description="Top 10 most active users", guild=discord.Object(id=GUILD_ID))
async def message_leaderboard(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    if guild_id not in message_counts or not message_counts[guild_id]:
        await interaction.response.send_message("No messages yet!")
        return
    sorted_users = sorted(message_counts[guild_id].items(), key=lambda x: x[1], reverse=True)[:10]
    embed = discord.Embed(
        title="🏆 Top 10 Chatters",
        description="Most active users in this server!",
        color=discord.Color.gold()
    )
    medals = ["🥇", "🥈", "🥉"] + ["#4️⃣", "#5️⃣", "#6️⃣", "#7️⃣", "#8️⃣", "#9️⃣", "#🔟"]
    for i, (user_id, count) in enumerate(sorted_users):
        member = interaction.guild.get_member(int(user_id))
        if member:
            name = member.display_name
            avatar_url = member.display_avatar.url
        else:
            name = f"User {user_id}"
            avatar_url = discord.Embed.Empty
        embed.add_field(
            name=f"{medals[i]} {name}",
            value=f"Messages: **{count}**",
            inline=False
        )
        if member and i == 0:
            embed.set_thumbnail(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# /add_message: visible and functional for mods/admins
@tree.command(name="add_message", description="Add messages to a user (mods/admins only)", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="The member to add messages to", amount="How many messages to add")
async def add_message(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not (interaction.user.guild_permissions.manage_messages or interaction.user.guild_permissions.administrator):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("Please enter a positive number.", ephemeral=True)
        return
    new_count = add_user_count(interaction.guild.id, member.id, amount)
    embed = discord.Embed(
        title="Message Count Updated",
        description=f"Added {amount} messages to {member.mention}.\nNew count: **{new_count}**",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)
    # Check for milestones
    class DummyMsg:
        def __init__(self, author, guild, channel):
            self.author = author
            self.guild = guild
            self.channel = channel
    await check_milestone(DummyMsg(member, interaction.guild, interaction.channel), new_count)

# /remove_message: visible and functional for mods/admins
@tree.command(name="remove_message", description="Remove messages from a user (mods/admins only)", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="The member to remove messages from", amount="How many messages to remove")
async def remove_message(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not (interaction.user.guild_permissions.manage_messages or interaction.user.guild_permissions.administrator):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("Please enter a positive number.", ephemeral=True)
        return
    new_count = remove_user_count(interaction.guild.id, member.id, amount)
    embed = discord.Embed(
        title="Message Count Updated",
        description=f"Removed {amount} messages from {member.mention}.\nNew count: **{new_count}**",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

bot.run(bot token)
