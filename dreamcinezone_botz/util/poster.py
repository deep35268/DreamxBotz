from PIL import Image, ImageDraw, ImageFont
import aiohttp
from io import BytesIO
from database.Imdbposter import get_movie_details
import logging

logger = logging.getLogger(__name__)

async def get_poster_with_rating(file_name):
    try:
        # ਫਾਈਲ ਨਾਮ ਤੋਂ ਮੂਵੀ ਟਾਈਟਲ ਲੈਣਾ
        movie_title = file_name.split(' - ')[0].split('[')[0].strip()
        if not movie_title or len(movie_title) < 3:
            return None, None

        movie = await get_movie_details(movie_title)
        if not movie or not movie.get('poster_url') or not movie.get('rating'):
            return None, None

        rating = movie['rating']
        poster_url = movie['poster_url']

        async with aiohttp.ClientSession() as session:
            async with session.get(poster_url) as resp:
                if resp.status != 200:
                    return None, None
                img_data = await resp.read()

        img = Image.open(BytesIO(img_data)).convert("RGB")
        draw = ImageDraw.Draw(img)

        # ਫੌਂਟ ਲੋਡ ਕਰਨ ਦੀ ਕੋਸ਼ਿਸ਼
        try:
            font = ImageFont.truetype("utils/fonts/arialbd.ttf", 55)
        except:
            try:
                font = ImageFont.truetype("utils/fonts/arial.ttf", 55)
            except:
                font = ImageFont.load_default()

        text = f"⭐ {rating}"
        text_width = draw.textlength(text, font=font)
        
        # ਹੇਠਾਂ ਸੱਜੇ ਪਾਸੇ ਰੇਟਿੰਗ ਲਿਖੋ
        x = img.width - text_width - 30
        y = img.height - 90
        draw.text((x, y), text, fill=(255, 215, 0), font=font, 
                 stroke_width=4, stroke_fill=(0, 0, 0))

        output = BytesIO()
        img.save(output, format='JPEG', quality=92)
        output.seek(0)

        return output, movie

    except Exception as e:
        logger.error(f"Poster with rating error: {e}")
        return None, None
