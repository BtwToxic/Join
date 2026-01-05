import asyncio
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
import pyrogram
print("Library:", pyrogram.__name__)
print("Version:", pyrogram.__version__)
# ─────────────────────────────
# CONFIG
# ─────────────────────────────
API_ID = 29170645
API_HASH = "0498ddbf04f71f7d91018c27140b82b3"
BOT_TOKEN = "8094733589:AAGg3nkrh8yT6w5C7ySbV7C54bE5n6lyeCg"

app = Client(
    "auto_accept_delay_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ─────────────────────────────
# DELAY STORAGE (PER GROUP)
# ─────────────────────────────
JOIN_DELAY = {}   # chat_id : seconds


# ─────────────────────────────
# 🔐 ADMIN / OWNER CHECK (FINAL)
# ─────────────────────────────
async def is_admin(client, chat_id, user_id):
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in ("administrator", "creator")


# ─────────────────────────────
# /delay COMMAND (ADMIN ONLY)
# ─────────────────────────────
@app.on_message(filters.command("delay") & filters.group)
async def set_delay(client, message):
    if message.from_user is None:
        return await message.reply_text(
            "❌ Anonymous admin detected.\n"
            "Remain Anonymous OFF karo."
        )

    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        return await message.reply_text(
            "❌ Sirf admins / owner delay set kar sakte hain."
        )

    if len(message.command) != 2:
        return await message.reply_text(
            "❌ Usage: `/delay <minutes>`\nExample: `/delay 1`"
        )

    try:
        minutes = int(message.command[1])
        if minutes < 0 or minutes > 1440:
            raise ValueError
    except ValueError:
        return await message.reply_text(
            "❌ Minutes 0–1440 ke beech hone chahiye."
        )

    JOIN_DELAY[chat_id] = minutes * 60

    if minutes == 0:
        await message.reply_text("✅ Delay **OFF** kar diya gaya hai.")
    else:
        await message.reply_text(
            f"✅ Join request delay set: **{minutes} minute(s)**"
        )


# ─────────────────────────────
# AUTO ACCEPT JOIN REQUEST
# ─────────────────────────────
@app.on_chat_join_request()
async def auto_accept(client: Client, request: ChatJoinRequest):
    chat_id = request.chat.id
    user = request.from_user
    chat = request.chat

    delay = JOIN_DELAY.get(chat_id, 0)

    # ⏳ Delay
    if delay > 0:
        await asyncio.sleep(delay)

    # ✅ Accept request
    try:
        await request.approve()
    except:
        return  # already approved / expired

    # 📩 DM user
    try:
        await client.send_message(
            user.id,
            f"✅ **Your request has been accepted successfully!**\n\n"
            f"👥 Group: **{chat.title}**\n"
            f"⏱️ Delay: {delay // 60} minute(s)\n\n"
            "🎉 Welcome!"
        )
    except:
        pass

    # (Optional) Group welcome
    try:
        await client.send_message(
            chat.id,
            f"👋 {user.mention} joined the group."
        )
    except:
        pass


print("🤖 Auto Accept + Delay Bot Started")
app.run()
