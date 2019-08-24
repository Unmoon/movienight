import configparser
import os

import appdirs

CONFIG_DIR = appdirs.user_config_dir("Movie Night", "Unmoon")


class SimpleConfig(configparser.ConfigParser):
    def get(self, option, section="DEFAULT", **kwargs):
        return super(SimpleConfig, self).get(option=option, section=section, **kwargs)

    def set(self, option, value, section="DEFAULT"):
        return super(SimpleConfig, self).set(
            option=option, value=value, section=section
        )

    def write(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        with open(os.path.join(CONFIG_DIR, "config.ini"), "w") as configfile:
            super(SimpleConfig, self).write(configfile)


def read_config():
    filename = os.path.join(CONFIG_DIR, "config.ini")
    if not os.path.isfile(filename):
        data = (
            "[DEFAULT]\n"
            "version = 0.1\n"
            "sync_server = unmoon.com\n"
            "file_server = https://unmoon.com/dl/\n"
            "files = []\n"
        )
        config.read_string(data)
        print("Default config loaded.")
    else:
        print("Config read from file:", config.read(filename))


config = SimpleConfig()
read_config()
