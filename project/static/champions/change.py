from os import listdir
from PIL import Image

for i in listdir("."):
    if not i.endswith(".py"):
        image = Image.open(i)
        new_image = image.resize((50, 50))
        new_image.save(i)