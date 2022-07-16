from starlette.responses import JSONResponse
from config import config
from database import get_or_none, users, tokens, manager
from constants import perms
from PIL import Image, ImageSequence
# import images2gif
from gifUtil import resize_gif
import hashlib
import io, os

allowed_formats = ["GIF", "JPEG", "PNG"]

async def handler(request):
    form_data = await request.form()
    rt_raw = hashlib.md5(form_data.get("rt", "").encode())
    rt = rt_raw.hexdigest()
    token_info = await get_or_none(tokens, token=rt)
    if token_info is None:
        return JSONResponse({'error': 'You are not authorized! Or token not found'})

    user = await get_or_none(users, id=token_info.user)
    if not user:
        return JSONResponse({'error': f'User with id {token_info.user} not found in database!'})

    form_data = await request.form()
    if form_data.get("avatar", None) is None:
        return JSONResponse({'error': 'Avatar not found'})

    content_length = int(request.headers.get('content-length', 0))
    if not content_length or content_length > 10240000:
        return JSONResponse({'error': 'Avatar should be less 10.24MB'})

    img_object = await form_data["avatar"].read()
    try:
        img = Image.open(io.BytesIO(img_object))
    except Exception:
        return JSONResponse({'error': 'Image is corrupted'})

    if img.format not in allowed_formats:
        return JSONResponse({'error': 'This file type is not allowed on server. You can upload only GIF, PNG, JPG images'})

    if img.format == "GIF":
        if config['enableGifs'] is False:
            return JSONResponse({'error': 'Sorry, but now you can\'t upload GIF images. (server disallowed)'})

        if config['enableDonorGifs']:
            if not (user.privileges & perms.USER_DONOR) > 0:
                return JSONResponse({'error': 'You are not allowed to upload avatar (this feature enabled only for donors)'})
    else:
        if img.size[0] != img.size[1]:
            return JSONResponse({'error': 'Image should have square form (like 256x256)'})

    if img.size[0] > 256 or img.size[1] > 256:
        if img.format != "GIF":
            img = img.resize((256, 256), Image.ANTIALIAS)
            print(img.size)
        else:
            return JSONResponse({'error': 'Some of dimension have more than 256px'})

    # Remove old avatars
    if os.path.isfile(f"{config['avatar_dir']}/{user.id}.png"):
        os.remove(f"{config['avatar_dir']}/{user.id}.png")
    if os.path.isfile(f"{config['avatar_dir']}/{user.id}.gif"):
        os.remove(f"{config['avatar_dir']}/{user.id}.gif")

    if img.format == "GIF":
        new_avatar = open(f"{config['avatar_dir']}/{user.id}.gif", mode="wb")
        new_avatar.write(img_object)
        new_avatar.close()
    else:
        #new_avatar = open(f"{config['avatar_dir']}/{user.id}.png", mode="wb")
        img.save(f"{config['avatar_dir']}/{user.id}.png", format="PNG")

    return JSONResponse({
        'response': 'Your avatar was successfully changed. It may take some time to properly update. To force a cache refresh, you can use CTRL+F5.'
    })
