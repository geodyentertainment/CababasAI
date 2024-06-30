import io
import requests
from PIL import Image
from discord import User
from discord import File

MURDER_PATH = 'resources/Images/CababasMurder.png'
MURDER_BG_PATH = 'resources/Images/CababasMurderBackground.png'
CABABAS_PATH = 'resources/Images/CababasNoMurder.png'

def get_pfp_as_bytes(user:User) -> bytes:
    with requests.get(user.avatar.url) as r:
        raw = r.content
    
    # with open('image_name.jpg', 'wb') as handler:
    #     handler.write(raw)    
    
    return raw
    
def get_pfp_as_image(user:User) -> Image.Image:
    raw_data = get_pfp_as_bytes(user)
    img = Image.open(io.BytesIO(raw_data))
    # img.show()
    
    return img

def image_to_file(img:Image.Image) -> File:
    with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            return File(image_binary,filename='pfp.png')

def murder(user:User,refuse:bool|None = False) -> Image.Image:
    pfp = get_pfp_as_image(user).convert('RGBA')
    if refuse:
        murder_img = Image.open(CABABAS_PATH).convert('RGBA')
    else:
        murder_img = Image.open(MURDER_PATH).convert('RGBA')
    
    bg = Image.open(MURDER_BG_PATH).convert('RGBA')
    
    w,h = bg.size
    
    new_murder_img = murder_img.resize((int(h),int(h))).rotate(-10,Image.Resampling.BILINEAR)
    new_pfp = pfp.resize(
        (int(h/1.5),int(h/1.5))
    )
    pfp.close()
    murder_img.close()
    
    murder_img_offset = (
        int(w-new_murder_img.size[0]-(w*0.1)),
        int((h-new_murder_img.size[1])/2)
    )
    pfp_offset = (
        int(w*0.1),
        int((h-new_pfp.size[1])/2)
    )
    
    bg.paste(new_pfp, pfp_offset, new_pfp)
    bg.paste(new_murder_img, murder_img_offset, new_murder_img)

    return bg