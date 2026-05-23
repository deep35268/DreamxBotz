from pyrogram import Client, filters
from info import CHANNELS
from database.ia_filterdb import save_file
from utils.poster import get_poster_with_rating   # ← ਇਹ ਲਾਈਨ ਐਡ ਕਰੋ

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

    # ⭐ ਨਵਾਂ ਫੀਚਰ - ਪੋਸਟਰ ਉੱਤੇ ਰੇਟਿੰਗ ਲਗਾਉਣਾ
    if media.file_type == "video" or media.file_type == "document":
        try:
            # ਫਾਈਲ ਨਾਮ ਤੋਂ ਮੂਵੀ ਨਾਮ ਲੈਣਾ
            file_name = media.file_name or "Unknown"
            poster, movie_data = await get_poster_with_rating(file_name)
            
            if poster and movie_data:
                # ਨਵਾਂ ਪੋਸਟਰ ਭੇਜਣ ਲਈ
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=poster,
                    caption=media.caption or file_name,
                    parse_mode='html'
                )
                # ਓਰਿਜਨਲ ਫਾਈਲ ਵੀ ਸੇਵ ਕਰੋ
                await save_file(bot, media)
                return
        except Exception as e:
            print(f"Poster Generation Error: {e}")

    # ਆਮ ਫਾਈਲ ਸੇਵ ਕਰੋ (ਜੇ ਪੋਸਟਰ ਨਾ ਬਣਿਆ ਤਾਂ)
    await save_file(bot, media)
