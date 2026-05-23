from PIL import Image, ImageDraw, ImageFont
import aiohttp
from io import BytesIO
from database.Imdbposter import get_movie_details

async def add_rating_to_poster(movie_name, poster_url):
    try:
        movie = await get_movie_details(movie_name)
        if not movie or not movie.get('rating'):
            return None

        rating = movie['rating']
        
        async with aiohttp.ClientSession() as session:
            async with session.get(poster_url) as resp:
                if resp.status != 200:
                    return None
                img_data = await resp.read()

        img = Image.open(BytesIO(img_data))
        draw = ImageDraw.Draw(img)

        # ਫੌਂਟ ਲੋਡ ਕਰੋ (ਬੋਟ ਵਿੱਚ fonts ਫੋਲਡਰ ਬਣਾ ਲਓ)
        try:
            font = ImageFont.truetype("utils/fonts/arial.ttf", 45)
        except:
            font = ImageFont.load_default()

        # ਰੇਟਿੰਗ ਲਿਖੋ (ਹੇਠਾਂ ਸੱਜੇ ਪਾਸੇ)
        text = f"⭐ {rating}"
        draw.text((img.width - 180, img.height - 80), text, fill=(255, 215, 0), font=font, stroke_width=2, stroke_fill=(0,0,0))

        output = BytesIO()
        img.save(output, format='JPEG')
        output.seek(0)
        return output

    except Exception as e:
        print(f"Poster Rating Error: {e}")
        return None
