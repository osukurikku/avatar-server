from starlette.responses import FileResponse, StreamingResponse
from config import config
from PIL import Image, ImageDraw
from PIL import GifImagePlugin

import os, io

if not os.path.exists(config['avatar_dir']):
    os.makedirs(config['avatar_dir'], 0o770) # Create folder with full priviliges(maybe idk ;d)
    empty_image = Image.new('RGB', (250, 250), color=(73, 109, 137))
 
    d = ImageDraw.Draw(empty_image)
    d.text((10,10), "Hello, another epic ripple server", fill=(255,255,255))
    empty_image.save(f"{config['avatar_dir']}/999.png", format="PNG")

async def handler(request):
    user_id = request.path_params['id']
    isOsu = request.headers.get("user-agent", "") == "osu!"

    # Let check is gif avatar?
    if os.path.isfile(f"{config['avatar_dir']}/{user_id}.png"):
        # Okay picture, i send you to user!
        return FileResponse(f"{config['avatar_dir']}/{user_id}.png")

    if os.path.isfile(f"{config['avatar_dir']}/{user_id}.gif"):
        if isOsu:
            # It's osu send to client one thing FIRST FRAME OF GIF
            gif_object = Image.open(f"{config['avatar_dir']}/{user_id}.gif")
            buffer = io.BytesIO()
            if gif_object.is_animated:
                gif_object.seek(0)
                gif_object.save(buffer, format="PNG")
                buffer.seek(0)
            else:
                # Fake gif, or not animated ;d
                gif_object.save(buffer, format="PNG")
                buffer.seek(0)

            return StreamingResponse(buffer, media_type="image/png")
        else:
            # It's just a website or another source
            return FileResponse(f"{config['avatar_dir']}/{user_id}.gif")
    
    # We are not found anything, than send default 999.png!
    return FileResponse(f"{config['avatar_dir']}/999.png")