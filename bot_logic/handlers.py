import re
import html
from telegram import Update
from telegram.ext import ContextTypes
from .utils import load_categories, get_category_members

MENTION_RE = re.compile(r'(?<!\S)@([\w-]+)')

async def mention_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: mention_handler entered")
    if not update.message or not update.message.text:
        print("DEBUG: no message or no text")
        return

    chat_id = update.effective_chat.id
    text = update.message.text.lower()

    mentions = [m.group(1) for m in MENTION_RE.finditer(text)]
    if not mentions:
        print("DEBUG: no @mentions found")
        return

    cats = load_categories(chat_id)
    if not cats:
        print("DEBUG: no categories for this chat")
        return

    valid = [m for m in mentions if m in cats]
    if not valid:
        print("DEBUG: mentions found but none match categories in this chat:", mentions)
        return

    # Raccogli tutti gli utenti iscritti alle categorie menzionate
    to_notify = []
    for cat in valid:
        members = get_category_members(chat_id, cat) or []
        to_notify.extend(members)

    # Deduplica
    seen = set()
    to_notify_unique = []
    for uid in to_notify:
        if uid and uid not in seen:
            seen.add(uid)
            to_notify_unique.append(uid)

    if not to_notify_unique:
        await update.message.reply_text("Nessun iscritto alle categorie menzionate.")
        return

    # Recupera i nomi visibili degli utenti (se possibile)
    mention_texts = []
    for uid in to_notify_unique:
        try:
            member = await context.bot.get_chat_member(chat_id, uid)
            name = html.escape(member.user.first_name or "Utente")
        except Exception as e:
            print(f"DEBUG: errore nel recupero nome per {uid}:", e)
            name = f"User {uid}"

        mention_texts.append(f"👤 <a href=\"tg://user?id={uid}\">{name}</a>")

    mentions_html = " ".join(mention_texts)
    cats_str = ", ".join(f"@{c}" for c in valid)

    reply_text = f"Notifica per le categorie: {html.escape(cats_str)}\n{mentions_html}"

    try:
        await update.message.reply_text(
            reply_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        print("ERROR sending mention reply:", e)
