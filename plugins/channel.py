from pyrogram import Client, filters
from info import CHANNELS
from database.ia_filterdb import save_file
from database.Imdbposter import get_movie_details, fetch_image
import logging

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
    logger.info(f"📥 ਨਵੀਂ ਫਾਈਲ ਆਈ: {file_name}")

    # IMDb Poster + Rating
    if media.file_type in ["video", "document"]:
        try:
            clean_title = file_name.split(' - ')[0].split('[')[0].strip()
            logger.info(f"🔍 IMDb ਖੋਜ ਰਿਹਾ ਹਾਂ: {clean_title}")

            movie = await get_movie_details(clean_title)
            
            if movie:
                rating = movie.get('rating', 'N/A')
                poster_url = movie.get('poster_url')
                logger.info(f"✅ IMDb ਡਾਟਾ ਮਿਲਿਆ | ਰੇਟਿੰਗ: {rating}")

                if poster_url:
                    logger.info("🖼️ ਪੋਸਟਰ ਬਣਾ ਰਿਹਾ ਹਾਂ...")
                    resized_poster = await fetch_image(poster_url, rating=rating)
                    
                    if resized_poster:
                        logger.info("🎉 ਪੋਸਟਰ ਬਣ ਗਿਆ! ਭੇਜ ਰਿਹਾ ਹਾਂ...")
                        await bot.send_photo(
                            chat_id=message.chat.id,
                            photo=resized_poster,
                            caption=media.caption or file_name
                        )
                        await save_file(bot, media)
                        return
                    else:
                        logger.warning("❌ ਪੋਸਟਰ ਬਣਾਉਣ ਵਿੱਚ ਫੇਲ")
            else:
                logger.warning("⚠️ IMDb ਡਾਟਾ ਨਹੀਂ ਮਿਲਿਆ")
        except Exception as e:
            logger.error(f"Poster Error: {e}")

    # Normal Save
    logger.info("💾 ਆਮ ਤਰੀਕੇ ਨਾਲ ਸੇਵ ਕਰ ਰਿਹਾ ਹਾਂ")
    await save_file(bot, media)
