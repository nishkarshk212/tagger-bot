from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import logging
import json
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# File to store user tags
TAGS_FILE = 'user_tags.json'

# Load existing tags
def load_tags():
    if os.path.exists(TAGS_FILE):
        with open(TAGS_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save tags to file
def save_tags(tags):
    with open(TAGS_FILE, 'w') as f:
        json.dump(tags, f)

# Available tags (you can customize these)
AVAILABLE_TAGS = {
    'developer': '👨‍💻 Developer',
    'designer': '🎨 Designer',
    'moderator': '🛡️ Moderator',
    'contributor': '🌟 Contributor',
    'vip': '⭐ VIP'
}

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Hi! I'm a user tagger bot. I help manage user tags in this group.\n\n"
        "Admins can use /taguser to assign tags to members."
    )

# Tag user command (admin only)
def tag_user(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        admin_user = update.message.from_user
        
        # Check if the command user is an admin
        chat_member = context.bot.get_chat_member(update.message.chat_id, admin_user.id)
        if chat_member.status not in ['administrator', 'creator']:
            update.message.reply_text("❌ Only admins can use this command.")
            return
            
        # Create inline keyboard with available tags
        keyboard = []
        for tag_id, tag_name in AVAILABLE_TAGS.items():
            keyboard.append([InlineKeyboardButton(tag_name, callback_data=f"tag_{target_user.id}_{tag_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            f"Select a tag for {target_user.full_name}:",
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text("⚠️ Please reply to a user's message with /taguser to tag them.")

# Callback handler for tag selection
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data.startswith('tag_'):
        _, user_id, tag_id = query.data.split('_')
        user_id = int(user_id)
        
        # Verify the admin is still an admin
        admin_user = query.from_user
        chat_member = context.bot.get_chat_member(query.message.chat_id, admin_user.id)
        if chat_member.status not in ['administrator', 'creator']:
            query.edit_message_text("❌ You're no longer an admin. Tag not applied.")
            return
            
        # Load and update tags
        tags = load_tags()
        if str(user_id) not in tags:
            tags[str(user_id)] = []
        
        if tag_id in tags[str(user_id)]:
            tags[str(user_id)].remove(tag_id)
            action = "removed"
        else:
            tags[str(user_id)].append(tag_id)
            action = "added"
        
        save_tags(tags)
        
        # Get the target user's name
        try:
            target_user = context.bot.get_chat_member(query.message.chat_id, user_id).user
            user_name = target_user.full_name
        except:
            user_name = "the user"
        
        # Update message
        tag_name = AVAILABLE_TAGS.get(tag_id, tag_id)
        query.edit_message_text(
            f"✅ {tag_name} tag {action} for {user_name}.\n\n"
            f"Now when you mention them, their tags will be displayed."
        )

# Show my tags command
def mytags(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    tags = load_tags()
    
    if str(user_id) in tags and tags[str(user_id)]:
        tag_names = [AVAILABLE_TAGS.get(tag, tag) for tag in tags[str(user_id)]]
        update.message.reply_text(f"Your tags: {', '.join(tag_names)}")
    else:
        update.message.reply_text("You don't have any tags yet.")

# Mention handler - shows tags when user is mentioned
def mention_handler(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        tags = load_tags()
        
        if str(user_id) in tags and tags[str(user_id)]:
            tag_names = [AVAILABLE_TAGS.get(tag, tag) for tag in tags[str(user_id)]]
            update.message.reply_text(
                f"🏷️ Tags: {', '.join(tag_names)}",
                reply_to_message_id=update.message.reply_to_message.message_id
            )

def error(update: Update, context: CallbackContext):
    logger.warning(f'Update {update} caused error {context.error}')

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("7548400379:AAFChkgOoAS8Gr3J1AcCuSrWXMH9FKR7Ucw", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("taguser", tag_user))
    dp.add_handler(CommandHandler("mytags", mytags))
    
    # Add callback handler for buttons
    dp.add_handler(CallbackQueryHandler(button))
    
    # Add mention handler
    dp.add_handler(MessageHandler(Filters.reply, mention_handler))
    
    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()