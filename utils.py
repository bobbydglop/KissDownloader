import sys
import os
import configparser
from time import strftime, gmtime

class utils():
    def log(message, **options):
        tty = sys.stdout.isatty()
        if tty:
            print(message, **options)
        try:
            with open('kissdownloader.log', 'a') as f:
                current_time = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())
                f.write("%s\t%s\n" % (current_time, message))
        except Exception:
            print("=E Could not write to the log file")

    def get_config_path():
        if sys.platform == 'linux':
            config_folder = os.path.join(os.environ.get("HOME"), ".config", "kissdownloader")
        if sys.platform == 'win32':
            config_folder = os.path.join(os.environ.get("USERPROFILE"), "AppData\Roaming\kissdownloader")
        if sys.platform == 'darwin':
            config_folder = "/tmp"

        try:
            os.makedirs(config_folder)
        except OSError as e:
            if not os.path.isdir(config_folder):
                raise

        return config_folder

    def read_settings():
        cfg = configparser.ConfigParser()
        config_file = os.path.join(utils.get_config_path(), "kissdownloader.ini")
        try:
            with open(config_file, 'r') as f:
                cfg.read(config_file)
            return cfg
        except FileNotFoundError:
            utils.log("Couldn't open {0}.\nCreating new settings file.".format(config_file))
            # try to create the config file with default settings and return them
            cfg['DEFAULT'] = {  'username': 'kiss-downloader',
                                'userpassword': 'Z4J2tIb1f2y6',
                                'destination_folder': '',
                              }
            cfg['OTHER'] = {    'download_threads': '4',
                                'demo_data': '1',
                                'complete_dir': '',
                            }
            utils.write_settings(cfg)
            return cfg
        except KeyError:
            utils.log("Couldn't open settings file {0}".format(config_file))
        except Exception as e:
            utils.log("Couldn't open settings file {0}: {1}".format(config_file, e))
        return None

    def write_settings(cfg):
        config_file = os.path.join(utils.get_config_path(), "kissdownloader.ini")
        with open(config_file, 'w') as cf:
            cfg.write(cf)

    def sanitize_filename(filename):
        """
        Removes characters that Windows CMD is unable to display
        """
        return ''.join([char for char in filename if char in '0123456789aâbcdefghiîjklmnopqrstuvwxyzAÂBCDEFGHIÎJKLMNOPQRSTUVWXYZ[](){}.,-_!?@&%*+#^~ '])
