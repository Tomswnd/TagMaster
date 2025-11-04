from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .utils import create_category, add_user_to_category, load_categories, save_categories



async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra informazioni sul bot e sui comandi disponibili"""
    text = (
        "🤖 *Bot Categorie di Gruppo*\n\n"
        "Questo bot permette di creare *categorie di utenti* all'interno del gruppo Telegram, "
        "così da poter menzionare interi gruppi con una sola @.\n\n"
        "👨‍💻 *Creatore:* [@ityttmom](https://t.me/ityttmom)\n\n"
        "📜 *Comandi principali:*\n\n"
        "• `/creacategoria <nome>` — Crea una nuova categoria.\n\n"
        "• `/iscrivi <nome_categoria>` — Ti iscrive a una categoria.\n\n"
        "• `/aggiungi <nome_categoria> <@utente>` — (solo admin) aggiunge un utente a una categoria.\n\n"
        "• `/listacategorie` — Mostra tutte le categorie e i relativi iscritti.\n\n"
        "• `/eliminacategoria <nome_categoria>` — (solo admin) elimina una categoria, con conferma.\n\n"
        "💬 *Come funziona:*\n"
        "Scrivi `@<nome_categoria>` in chat per menzionare automaticamente tutti gli utenti iscritti a quella categoria."
    )

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)





async def create_category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # controlla che sia in un gruppo
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Questo comando può essere usato solo in un gruppo.")
        return

    # controlla che ci sia un argomento
    if len(context.args) < 1:
        await update.message.reply_text("Uso: /createcategoria <nome>")
        return

    category = context.args[0].lower()
    chat_id = str(update.effective_chat.id)  # ogni gruppo ha un id diverso
    user_id = update.effective_user.id

    # crea la categoria per quel gruppo
    if create_category(chat_id, category, user_id):
        await update.message.reply_text(f"✅ Categoria '{category}' creata per questo gruppo!")
    else:
        await update.message.reply_text("⚠️ Categoria già esistente in questo gruppo.")


async def join_category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # controlla che sia in un gruppo
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Questo comando può essere usato solo in un gruppo.")
        return
    if len(context.args) < 1:
        await update.message.reply_text("Uso: /iscrivi <categoria>")
        return
    category = context.args[0].lower()
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    success = add_user_to_category(chat_id, category, user_id)
    if success:
        await update.message.reply_text(f"✅ Ti sei iscritto a '{category}'!")
    else:
        await update.message.reply_text("⚠️ Categoria non trovata. Crea prima con /createcategoria.")

async def list_categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # controlla che sia in un gruppo
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Questo comando può essere usato solo in un gruppo.")
        return
    chat_id = update.effective_chat.id
    cats = load_categories(chat_id)
    if not cats:
        await update.message.reply_text("Nessuna categoria creata.")
        return
    text = "📂 Categorie disponibili:\n" + "\n".join(f"- {c}" for c in cats.keys())
    await update.message.reply_text(text)


async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Permette a un admin di aggiungere un altro utente a una categoria"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Controlla se l'utente è admin
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status not in ["administrator", "creator"]:
            await update.message.reply_text("❌ Solo un admin può usare questo comando.")
            return
    except Exception:
        await update.message.reply_text("Errore nel verificare i permessi.")
        return

    # Controlla sintassi: /aggiungi <categoria> <@utente o user_id>
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /aggiungi <categoria> <@utente o user_id>")
        return

    category = context.args[0].lower()
    target_arg = context.args[1]

    # Carica categorie per il gruppo
    categories = load_categories(chat_id)
    if category not in categories:
        await update.message.reply_text(f"⚠️ Categoria '{category}' non esiste.")
        return

    # Ricava user_id dell'utente da aggiungere
    if target_arg.startswith("@"):
        # Se menzione, usa get_chat_member
        username = target_arg[1:]
        try:
            # Cerca nella chat il membro con username
            members = await context.bot.get_chat_administrators(chat_id)  # workaround per cercare utenti, in alternativa get_chat_member singolo se ID noto
            target_id = None
            for m in members:
                if m.user.username and m.user.username.lower() == username.lower():
                    target_id = m.user.id
                    break
            if not target_id:
                await update.message.reply_text(f"⚠️ Utente @{username} non trovato.")
                return
        except Exception as e:
            await update.message.reply_text("Errore nel recuperare l'utente.")
            return
    else:
        # Se passano direttamente un ID
        try:
            target_id = int(target_arg)
        except ValueError:
            await update.message.reply_text("⚠️ Inserisci un user_id valido o menzione.")
            return

    # Aggiungi l'utente alla categoria
    success = add_user_to_category(chat_id, category, target_id)
    if success:
        await update.message.reply_text(f"✅ Utente aggiunto alla categoria '{category}'.")
    else:
        await update.message.reply_text(f"⚠️ Utente già presente o categoria inesistente.")


async def delete_category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /eliminacategoria <categoria>: chiede conferma con pulsanti"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # verifica permessi admin
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status not in ["administrator", "creator"]:
            await update.message.reply_text("❌ Solo un admin può eliminare categorie.")
            return
    except Exception:
        await update.message.reply_text("Errore nel verificare i permessi.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Uso: /eliminacategoria <nome_categoria>")
        return

    category = context.args[0].lower()
    cats = load_categories(chat_id)

    if category not in cats:
        await update.message.reply_text(f"⚠️ La categoria '{category}' non esiste.")
        return

    # Crea tastiera inline con conferma/annulla
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Conferma", callback_data=f"confirm_delete|{chat_id}|{category}|{user_id}"),
            InlineKeyboardButton("❌ Annulla", callback_data=f"cancel_delete|{user_id}")
        ]
    ])

    await update.message.reply_text(
        f"⚠️ Sei sicuro di voler eliminare la categoria '{category}'?",
        reply_markup=keyboard
    )


async def handle_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce la conferma o l'annullamento dell'eliminazione"""
    query = update.callback_query
    await query.answer()  # necessario per chiudere il "caricamento"

    data = query.data.split("|")
    action = data[0]

    if action == "confirm_delete":
        _, chat_id, category, requested_by = data
        chat_id = int(chat_id)
        requested_by = int(requested_by)

        # verifica che chi clicca sia lo stesso admin
        if query.from_user.id != requested_by:
            await query.edit_message_text("❌ Solo chi ha richiesto l'eliminazione può confermarla.")
            return

        cats = load_categories(chat_id)
        if category not in cats:
            await query.edit_message_text(f"⚠️ La categoria '{category}' non esiste più.")
            return

        del cats[category]
        save_categories(chat_id, cats)
        await query.edit_message_text(f"✅ Categoria '{category}' eliminata con successo.")

    elif action == "cancel_delete":
        _, requested_by = data
        requested_by = int(requested_by)

        if query.from_user.id != requested_by:
            await query.edit_message_text("❌ Solo chi ha richiesto l'eliminazione può annullare.")
            return

        await query.edit_message_text("❌ Eliminazione annullata.")