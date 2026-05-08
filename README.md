# ⚡ HiddenGuard Bot

A premium Telegram group management bot with hidden admin system.

---

## 🚀 Deploy on Render (Free)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → **Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Add Environment Variable:
   - Key: `BOT_TOKEN`
   - Value: Your bot token from @BotFather
6. Click **Deploy** ✅

---

## 👑 Roles

| Role | Can Do |
|------|--------|
| Owner | Everything — add/remove all admins |
| Super Admin | Add/remove regular admins + mod commands |
| Admin | warn/mute/ban/unmute in group |
| Member | Normal user |

---

## 📋 Commands

### Mod Commands (Admin+)
> Use in GC by **replying** to a user's message

| Command | Action |
|---------|--------|
| `/warn [reason]` | Warn user (auto-ban at 3) |
| `/mute [reason]` | Mute user |
| `/unmute` | Unmute user |
| `/ban [reason]` | Ban user |
| `/warns` | Check warn count |
| `/unwarn` | Clear warns |

### Admin Controls (Super Admin+)
| Command | Action |
|---------|--------|
| `/addadmin` | Add admin (reply to user) |
| `/addsuperadmin` | Add super admin (owner only) |
| `/removeadmin` | Remove admin (owner only) |
| `/adminlist` | View all admins (sent to DM) |

---

## ⚙️ Setup in Group

1. Add bot to your group
2. Make **only the bot** an admin (with all rights)
3. Remove admin from all real admins — they stay as normal members
4. Owner adds trusted people via `/addadmin` by replying to their message
5. Hidden admins use commands in group or DM — **no one will know!** 🔐

---

## 🔐 How It Stays Hidden

- Bot deletes the command message instantly in group
- Only the bot is Telegram admin — real admins look like normal members
- Actions (mute/ban/warn) still appear in group but no one knows who did it
