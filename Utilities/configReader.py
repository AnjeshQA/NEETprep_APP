import os
from configparser import ConfigParser


def readConfig(section, key):
    config = ConfigParser()

    # This creates an absolute path regardless of where you run the test from
    # It goes up one level from Utilities and into ConfigurationData
    current_dir = os.path.dirname(__file__)
    path = os.path.join(current_dir, "..", "ConfigurationData", "conf.ini")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Could not find conf.ini at {path}")

    config.read(path)
    return config.get(section, key)