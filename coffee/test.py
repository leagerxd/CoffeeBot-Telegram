from PIL import Image
from pathlib import Path
import pathlib
import os

BASE_DIR = Path(__file__).resolve().parent

desktop = pathlib.Path(BASE_DIR)
for item in desktop.iterdir():
    if item.is_dir():
        for item1 in item.iterdir():
            if item1.is_dir():
                for item2 in item1.dir():
                    img = Image(item2.path())
                    img.resi


files = os.listdir(BASE_DIR)
for file in os:
    print(file)

#    img = Image(filename)
#    img.resize()