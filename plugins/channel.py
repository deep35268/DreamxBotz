from pyrogram import Client, filters
from info import CHANNELS
from database.ia_filterdb import save_file
from utils.poster import get_poster_with_rating   # Poster with rating function
import logging

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

    # ⭐ ਪੋਸਟਰ ਉੱਤੇ IMDb ਰੇਟਿੰਗ ਲਗਾਉਣ ਵਾਲਾ ਫੀਚਰ
    if media.file_type in ["video", "document"]:
        try:
            file_name = media.file_name or "Unknown Movie"
            poster, movie_data = await get_poster_with_rating(file_name)
            
            if poster and movie_data:
                # ਰੇਟਿੰਗ ਵਾਲਾ ਪੋਸਟਰ ਚੈਨਲ ਵਿੱਚ ਭੇਜੋ
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=poster,
                    caption=media.caption or file_name,
                    parse_mode='html'
                )
                logger.info(f"Posted with IMDb rating poster: {file_name}")
                # ਓਰਿਜਨਲ ਫਾਈਲ ਵੀ ਡਾਟਾਬੇਸ ਵਿੱਚ ਸੇਵ ਕਰੋ
                await save_file(bot, media)
                return
                
        except Exception as e:
            logger.error(f"Poster generation error: {e}")

    # ਆਮ ਤਰੀਕੇ ਨਾਲ ਫਾਈਲ ਸੇਵ ਕਰੋ (ਜੇ ਪੋਸਟਰ ਨਾ ਬਣਿਆ ਤਾਂ)
    await save_file(bot, media)
