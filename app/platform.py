import os
from config import config


def getpath(path):
    base_path = os.path.join(config.upload_path, 'app', 'static',
                             'upload')
    UPLOAD_LICENCE_FOLDER = os.path.join(base_path, 'licence')
    UPLOAD_COVER_FOLDER = os.path.join(base_path, 'cover')
    UPLOAD_PIECE_FOLDER = os.path.join(base_path, 'pieceimg')
    UPLOAD_LIGHT_FOLDER = os.path.join(base_path, 'light')
    if path == "licence":
        return UPLOAD_LICENCE_FOLDER
    elif path == "cover":
        return UPLOAD_COVER_FOLDER
    elif path == "pieceimg":
        return UPLOAD_PIECE_FOLDER
    elif path == "light":
        return UPLOAD_LIGHT_FOLDER
    return path
