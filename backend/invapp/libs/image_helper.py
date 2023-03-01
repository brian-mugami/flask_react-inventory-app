import re
import os
from typing import Union
from werkzeug.datastructures import FileStorage

from flask_uploads import UploadSet, IMAGES

IMAGE_SET = UploadSet("images", IMAGES)
def save_image(image:FileStorage, folder:str = None, name:str = None) -> str:
    """Takes filestorage and saves it to a folder"""
    return IMAGE_SET.save(image, folder, name)
def get_path(filename:str, folder:str)->str:
    """Take image and folder and return full path"""
    return IMAGE_SET.path(filename, folder)

def find_image_in_any_format(filename: str, folder: str)->Union[str, None]:
    """Takes a filename and returns an image in any accepted formats"""
    for _format in IMAGES:
        image = f"{filename}.{_format}"
        image_path = IMAGE_SET.path(filename=image, folder=folder)
        if os.path.isfile(image_path):
            return image_path

    return None

def retrieve_filename(file: Union[str, FileStorage])->str:
    """Take filestorage and return the filename.
    allows function to take either fileStorage or filename and return a file name"""
    if isinstance(file, FileStorage):
        return file.filename
    return file

def is_filename_safe(file: Union[str, FileStorage])->bool:
    """Check regex and return whether the string matches or not"""
    filename = retrieve_filename(file)
    allowed_format = "|".join(IMAGES) #jpg|jpeg|png pipe in regex is or
    regex = f"^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({allowed_format})$"
    return re.match(regex, filename) is not None

def get_basename(file: Union[str, FileStorage])-> str:
    """Return full image name from path
    get basename(somefolder/image.jpg) returns image.jpg)"""

    filename = retrieve_filename(file)
    return os.path.split(filename)[1]
def get_extension(file: Union[str, FileStorage])-> str:
    """returns file extension
    get extension(image.jpg) returns '.jpg'"""
    filename = retrieve_filename(file)
    return os.path.splitext(filename)[1]