import re
import aiohttp
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from imdb import Cinemagoer
import logging

logger = logging.getLogger(__name__)

ia = Cinemagoer()
LONG_IMDB_DESCRIPTION = False

async def fetch_image(url, rating=None, size=(860, 1200)):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch image: {response.status}")
                    return None

                data = await response.read()
                img = Image.open(BytesIO(data)).convert("RGB")
                img = img.resize(size, Image.LANCZOS)

                if rating:
                    draw = ImageDraw.Draw(img)
                    try:
                        font = ImageFont.truetype("utils/fonts/arialbd.ttf", 60)
                    except:
                        font = ImageFont.load_default()

                    text = f"⭐ {rating}"
                    text_width = draw.textlength(text, font=font)
                    x = img.width - text_width - 40
                    y = img.height - 100
                    draw.text((x, y), text, fill=(255, 215, 0), font=font, stroke_width=4, stroke_fill=(0,0,0))

                output = BytesIO()
                img.save(output, format='JPEG', quality=92)
                output.seek(0)
                return output

    except Exception as e:
        logger.error(f"fetch_image error: {e}")
        return None


async def get_movie_details(query, id=False, file=None):
    try:
        if not id:
            query = query.strip().lower()
            title = query
            year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
            if year:
                year = year[0]
                title = query.replace(year, "").strip()
            elif file:
                year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
                if year:
                    year = year[0]

            search = ia.search_movie(title, results=10)
            if not search:
                return None

            if year:
                filtered = [m for m in search if str(m.get('year')) == str(year)]
                movie = filtered[0] if filtered else search[0]
            else:
                movie = search[0]

            movie = ia.get_movie(movie.movieID)
        else:
            movie = ia.get_movie(query)

        poster_url = movie.get('full-size cover url') or movie.get('cover url')

        return {
            'title': movie.get('title'),
            'rating': str(movie.get('rating')) if movie.get('rating') else "N/A",
            'poster_url': poster_url,
            'year': movie.get('year'),
            'genres': ", ".join(movie.get('genres', [])),
            'url': f"https://www.imdb.com/title/tt{movie.get('imdbID')}"
        }

    except Exception as e:
        logger.error(f"get_movie_details error: {e}")
        return None
