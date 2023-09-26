from configparser import ConfigParser


class AppConfiguration(ConfigParser):
    instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AppConfiguration, cls).__new__(cls)
            cls.instance.read('config.dblog')
        return cls.instance

    def save(self):
        self.instance.write('config.dblog')
