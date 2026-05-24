import re
import aiohttp
import logging
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

OMDB_API_KEY = "45502197"

async def fetch_image(url):
    """ਸਿਰਫ਼ ਪੋਸਟਰ ਡਾਊਨਲੋਡ ਕਰੋ (ਕੋਈ ਰੇਟਿੰਗ ਓਵਰਲੇ ਨਹੀਂ)"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.read()
                return BytesIO(data)
    except Exception as e:
        logger.error(f"fetch_image error: {e}")
        return None


async def get_movie_details(query):
    try:
        clean_query = re.sub(r'[\(\)\[\]\{\}]', '', query).strip()
        
        async with aiohttp.ClientSession() as session:
            url = f"http://www.omdbapi.com/?t={clean_query}&apikey={OMDB_API_KEY}"
            async with session.get(url) as resp:
                data = await resp.json()

        if data.get('Response') == 'False':
            return None

        return {
            'title': data.get('Title'),
            'poster_url': data.get('Poster') if data.get('Poster') != 'N/A' else None,
            'rating': data.get('imdbRating')
        }

    except Exception as e:
        logger.error(f"OMDB Error: {e}")
        return None
