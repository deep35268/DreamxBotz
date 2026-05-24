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

    # Clean Title
    clean_title = re.sub(r'\.\w{3,4}$', '', file_name)
    clean_title = re.sub(r'[\(\)\[\]\{\}]', ' ', clean_title)
    clean_title = re.sub(r'\d{4}', '', clean_title)
    clean_title = re.sub(r'[^a-zA-Z0-9\s]', ' ', clean_title).strip()

    logger.info(f"🧹 Clean Title: {clean_title}")

    if media.file_type in ["video", "document"]:
        try:
            movie = await get_movie_details(clean_title)
            if movie:
                rating = movie.get('rating', 'N/A')
                poster_url = movie.get('poster_url')

                if poster_url and rating != "N/A":
                    logger.info(f"🖼️ Poster ਬਣਾ ਰਿਹਾ ਹਾਂ... Rating: {rating}")
                    resized_poster = await fetch_image(poster_url, rating=rating)
                    
                    if resized_poster:
                        logger.info("🎉 Poster ਬਣ ਗਿਆ!")
                        await bot.send_photo(
                            chat_id=message.chat.id,
                            photo=resized_poster,
                            caption=media.caption or file_name
                        )
                        await save_file(bot, media)
                        return
        except Exception as e:
            logger.error(f"Poster Error: {e}")

    logger.info("💾 ਆਮ ਤਰੀਕੇ ਨਾਲ ਸੇਵ ਕੀਤਾ")
    await save_file(bot, media)
