import logging
import json
import os
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
OWNER_ID  = 5114938225
DB_FILE   = "data.json"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def load_db():
    if not os.path.exists(DB_FILE):
        return {"admins": [], "super_admins": [], "warns": {}}
    with open(DB_FILE) as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def is_bot_admin(uid):
    db = load_db()
    return uid == OWNER_ID or uid in db.get("admins", []) or uid in db.get("super_admins", [])

def is_super_admin(uid):
    db = load_db()
    return uid == OWNER_ID or uid in db.get("super_admins", [])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def silent_delete(update: Update):
    if update.effective_chat.type in ["group", "supergroup"]:
        try:
            await update.message.delete()
        except:
            pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  /start
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if chat.type in ["group", "supergroup"]:
        kb = [[InlineKeyboardButton("✅ Verify Me", callback_data=f"verify_{user.id}")]]
        await update.message.reply_text(
            f"👋 *Hey {user.first_name}!*\n"
            "━━━━━━━━━━━━━━━━━\n"
            "🔐 Tap below to verify yourself.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    is_owner = user.id == OWNER_ID
    is_sup   = is_super_admin(user.id)
    is_adm   = is_bot_admin(user.id)
    role     = "👑 Owner" if is_owner else "🌟 Super Admin" if is_sup else "🛡 Admin" if is_adm else "👤 Member"

    txt = (
        f"⚡ *HiddenGuard Bot*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 *You:* {user.first_name}\n"
        f"🏷 *Role:* {role}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )

    if is_adm:
        txt += (
            "\n📋 *Mod Commands*\n"
            "_(Reply to user's msg in GC)_\n\n"
            "⚠️ `/warn` `[reason]`\n"
            "🔇 `/mute` `[reason]`\n"
            "🔊 `/unmute`\n"
            "🚫 `/ban` `[reason]`\n"
            "📊 `/warns`\n"
            "🗑 `/unwarn`\n"
        )

    if is_sup:
        txt += (
            "\n👑 *Admin Controls*\n\n"
            "➕ `/addadmin` _(reply)_\n"
            "⭐ `/addsuperadmin` _(reply)_\n"
            "➖ `/removeadmin` _(reply, owner only)_\n"
            "📋 `/adminlist`\n"
        )

    if not is_adm:
        txt += "\n❌ *No admin access.*"

    await update.message.reply_text(txt, parse_mode="Markdown")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NEW MEMBER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def new_member(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        try:
            await ctx.bot.restrict_chat_member(
                update.effective_chat.id, member.id,
                ChatPermissions(can_send_messages=False)
            )
        except Exception as e:
            log.warning(f"Restrict failed: {e}")

        kb = [[InlineKeyboardButton("✅ Tap to Verify", callback_data=f"verify_{member.id}")]]
        await update.message.reply_text(
            f"👋 *Hey {member.first_name}!*\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🔐 Verify to start chatting!\n"
            f"⏳ Tap the button below!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  VERIFY CALLBACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def verify_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid   = int(query.data.split("_")[1])

    if query.from_user.id != uid:
        await query.answer("❌ Not for you!", show_alert=True)
        return

    try:
        await ctx.bot.restrict_chat_member(
            query.message.chat_id, uid,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await query.answer("✅ Verified! Welcome!", show_alert=True)
        await query.edit_message_text(
            f"✅ *{query.from_user.first_name}* is verified!\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🎉 Welcome to the group!",
            parse_mode="Markdown"
        )
    except Exception as e:
        await query.answer(f"❌ Error: {e}", show_alert=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  WARN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def warn(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if not is_bot_admin(user.id):
        await silent_delete(update)
        return

    await silent_delete(update)

    if not update.message.reply_to_message:
        await ctx.bot.send_message(user.id, "❌ *Reply to a user's message to warn.*", parse_mode="Markdown")
        return

    reason = " ".join(ctx.args) if ctx.args else "No reason provided"
    target = update.message.reply_to_message.from_user
    db     = load_db()
    tid    = str(target.id)
    db["warns"][tid] = db["warns"].get(tid, 0) + 1
    count  = db["warns"][tid]
    save_db(db)

    await chat.send_message(
        f"⚠️ *{target.first_name}* was warned!\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📌 *Reason:* {reason}\n"
        f"🔢 *Warns:* {count}/3",
        parse_mode="Markdown"
    )

    if count >= 3:
        try:
            await ctx.bot.ban_chat_member(chat.id, target.id)
            db["warns"][tid] = 0
            save_db(db)
            await chat.send_message(
                f"🚫 *{target.first_name}* auto-banned!\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"📌 *Reason:* 3 warns reached.",
                parse_mode="Markdown"
            )
        except Exception as e:
            log.error(f"Auto-ban failed: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MUTE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def mute(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if not is_bot_admin(user.id):
        await silent_delete(update)
        return

    await silent_delete(update)

    if not update.message.reply_to_message:
        await ctx.bot.send_message(user.id, "❌ *Reply to a user's message to mute.*", parse_mode="Markdown")
        return

    reason = " ".join(ctx.args) if ctx.args else "No reason provided"
    target = update.message.reply_to_message.from_user

    try:
        await ctx.bot.restrict_chat_member(
            chat.id, target.id,
            ChatPermissions(can_send_messages=False)
        )
        await chat.send_message(
            f"🔇 *{target.first_name}* was muted!\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📌 *Reason:* {reason}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await ctx.bot.send_message(user.id, f"❌ Mute failed: `{e}`", parse_mode="Markdown")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  UNMUTE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def unmute(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if not is_bot_admin(user.id):
        await silent_delete(update)
        return

    await silent_delete(update)

    if not update.message.reply_to_message:
        await ctx.bot.send_message(user.id, "❌ *Reply to a user's message to unmute.*", parse_mode="Markdown")
        return

    target = update.message.reply_to_message.from_user

    try:
        await ctx.bot.restrict_chat_member(
            chat.id, target.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await chat.send_message(
            f"🔊 *{target.first_name}* was unmuted!\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"✅ Free to chat again.",
            parse_mode="Markdown"
        )
    except Exception as e:
        await ctx.bot.send_message(user.id, f"❌ Unmute failed: `{e}`", parse_mode="Markdown")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BAN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def ban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if not is_bot_admin(user.id):
        await silent_delete(update)
        return

    await silent_delete(update)

    if not update.message.reply_to_message:
        await ctx.bot.send_message(user.id, "❌ *Reply to a user's message to ban.*", parse_mode="Markdown")
        return

    reason = " ".join(ctx.args) if ctx.args else "No reason provided"
    target = update.message.reply_to_message.from_user

    try:
        await ctx.bot.ban_chat_member(chat.id, target.id)
        await chat.send_message(
            f"🚫 *{target.first_name}* was banned!\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📌 *Reason:* {reason}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await ctx.bot.send_message(user.id, f"❌ Ban failed: `{e}`", parse_mode="Markdown")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  WARNS CHECK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def warns(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_bot_admin(user.id):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a user to check warns.")
        return
    target = update.message.reply_to_message.from_user
    db     = load_db()
    count  = db["warns"].get(str(target.id), 0)
    await update.message.reply_text(
        f"📊 *Warn Status*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 *User:* {target.first_name}\n"
        f"🔢 *Warns:* {count}/3",
        parse_mode="Markdown"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  UNWARN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def unwarn(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_bot_admin(user.id):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a user to clear warns.")
        return
    target = update.message.reply_to_message.from_user
    db     = load_db()
    db["warns"][str(target.id)] = 0
    save_db(db)
    await update.message.reply_text(
        f"🗑 *Warns Cleared!*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 *User:* {target.first_name}\n"
        f"✅ Warns reset to 0.",
        parse_mode="Markdown"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ADD ADMIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def addadmin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_super_admin(user.id):
        await update.message.reply_text("❌ Only *Super Admins* can add admins.", parse_mode="Markdown")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a user to add them.")
        return
    target = update.message.reply_to_message.from_user
    db     = load_db()
    if target.id in db["admins"] or target.id in db.get("super_admins", []) or target.id == OWNER_ID:
        await update.message.reply_text(f"⚠️ Already an admin!", parse_mode="Markdown")
        return
    db["admins"].append(target.id)
    save_db(db)
    await update.message.reply_text(
        f"✅ *{target.first_name}* added as Admin!\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🛡 Can now use mod commands.",
        parse_mode="Markdown"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ADD SUPER ADMIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def addsuperadmin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("❌ Only *Owner* can add Super Admins.", parse_mode="Markdown")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a user to promote them.")
        return
    target = update.message.reply_to_message.from_user
    db     = load_db()
    db.setdefault("super_admins", [])
    if target.id not in db["super_admins"]:
        db["super_admins"].append(target.id)
    if target.id in db.get("admins", []):
        db["admins"].remove(target.id)
    save_db(db)
    await update.message.reply_text(
        f"⭐ *{target.first_name}* is now Super Admin!\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🌟 Can add/remove admins.",
        parse_mode="Markdown"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  REMOVE ADMIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def removeadmin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("❌ Only *Owner* can remove admins.", parse_mode="Markdown")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a user to remove them.")
        return
    target  = update.message.reply_to_message.from_user
    db      = load_db()
    removed = False
    if target.id in db.get("admins", []):
        db["admins"].remove(target.id)
        removed = True
    if target.id in db.get("super_admins", []):
        db["super_admins"].remove(target.id)
        removed = True
    save_db(db)
    if removed:
        await update.message.reply_text(
            f"➖ *{target.first_name}* removed!\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 Back to normal member.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"⚠️ Not an admin.", parse_mode="Markdown")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ADMIN LIST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def adminlist(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_super_admin(user.id):
        await update.message.reply_text("❌ No permission.")
        return
    db           = load_db()
    admins       = db.get("admins", [])
    super_admins = db.get("super_admins", [])
    txt  = "📋 *Admin List*\n━━━━━━━━━━━━━━━━━\n\n"
    txt += f"👑 *Owner:* `{OWNER_ID}`\n\n"
    if super_admins:
        txt += "🌟 *Super Admins:*\n"
        for uid in super_admins:
            txt += f"  • `{uid}`\n"
        txt += "\n"
    txt += "🛡 *Admins:*\n"
    if admins:
        for uid in admins:
            txt += f"  • `{uid}`\n"
    else:
        txt += "  _None yet_\n"
    await ctx.bot.send_message(user.id, txt, parse_mode="Markdown")
    if update.effective_chat.type != "private":
        await update.message.reply_text("📬 *List sent to your DM!*", parse_mode="Markdown")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",         start))
    app.add_handler(CommandHandler("warn",          warn))
    app.add_handler(CommandHandler("mute",          mute))
    app.add_handler(CommandHandler("unmute",        unmute))
    app.add_handler(CommandHandler("ban",           ban))
    app.add_handler(CommandHandler("warns",         warns))
    app.add_handler(CommandHandler("unwarn",        unwarn))
    app.add_handler(CommandHandler("addadmin",      addadmin))
    app.add_handler(CommandHandler("addsuperadmin", addsuperadmin))
    app.add_handler(CommandHandler("removeadmin",   removeadmin))
    app.add_handler(CommandHandler("adminlist",     adminlist))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify_"))

    log.info("🤖 HiddenGuard Bot is running!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
