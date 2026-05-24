from pyrogram import Client, filters
from info import CHANNELS
from database.ia_filterdb import save_file
from database.Imdbposter import get_movie_details, fetch_image
import logging
import re

logger = logging.getLogger(__name__)

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    """Media Handler"""
    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    media.file_type = file_type
    media.caption = message.caption

    file_name = media.file_name or "Unknown"
    logger.info(f"📥 ਨਵੀਂ ਫਾਈਲ: {file_name}")

    # Title Clean
    clean_title = re.sub(r'\.\w{3,4}$', '', file_name)
    clean_title = re.sub(r'[\(\)\[\]\{\}]', ' ', clean_title)
    clean_title = re.sub(r'[^a-zA-Z0-9\s]', ' ', clean_title).strip()

    logger.info(f"🧹 Clean Title: {clean_title}")

    # ਸਿਰਫ਼ ਪੋਸਟਰ ਲੈਣ ਵਾਲਾ ਭਾਗ
    if media.file_type in ["video", "document"]:
        try:
            movie = await get_movie_details(clean_title)
            if movie and movie.get('poster_url'):
                logger.info("🖼️ ਪੋਸਟਰ ਲੱਭਿਆ, ਭੇਜ ਰਿਹਾ ਹਾਂ...")
                poster = await fetch_image(movie.get('poster_url'))
                
                if poster:
                    await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=poster,
                        caption=media.caption or file_name
                    )
                    await save_file(bot, media)
                    return
        except Exception as e:
            logger.error(f"Poster Error: {e}")

    # ਆਮ ਫਾਈਲ ਸੇਵ
    logger.info("💾 ਆਮ ਤਰੀਕੇ ਨਾਲ ਸੇਵ ਕੀਤਾ")
    await save_file(bot, media)
