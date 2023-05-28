import re
import os
import sys


def extract_placeholder(text):
    """Extract the variable occupying symbol in the string"""
    pattern = r"\{(\w+)\}"
    return re.findall(pattern, text)


def mkdirs(path):
    dir = os.path.dirname(path)
    os.makedirs(dir, exist_ok=True)
    # only the UNIX system can execute file permissions change
    if sys.platform in ["linux", "darwin"]:
        os.chown(dir, os.getuid(), os.getgid())


def fix_dict_identifier(map: dict) -> dict:
    """
    Fixed the key of the map: Some key is with. For example, user.user_id.
    But functions such as Format in Python do not support the logo of the point,
    This method is to remove the prefix of the key and only retain the later part as the key of the map.
    """
    return {k.split(".")[1]: v for k, v in map.items() if "." in k}
