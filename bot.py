import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
import subprocess
import yt_dlp
import os
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Send me a URL to download the image or a video from youtube.")


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    if not url.startswith('http'):
        await update.message.reply_text("Please send a valid URL.")
        return
    if url.startswith('https://www.youtube.com/watch?v='):
        try:
            output_filename = "video.mp4"
            subprocess.run(["yt-dlp","--recode-video",  "mp4",  "--merge-output-format", "mp4", "-o", output_filename, url])
            
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open(output_filename, 'rb'))
            os.remove(output_filename)
        except Exception as e:
            print('An error occurred:', e)
    else:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open('image.jpg', 'wb') as file:
                    file.write(response.content)
                await context.bot.send_document(chat_id=update.effective_chat.id, document=open('image.jpg', 'rb'))
        except Exception as e:
            print('An error occurred:', e)


def main() -> None:
    application = Application.builder().token("6793255096:AAE9PUSmqFBEwf5dYzuLAsmbrpDfQvENgaw").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()