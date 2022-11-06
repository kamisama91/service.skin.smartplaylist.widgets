import helper

class Settings:
    __instance = None
    MAX_ITEM = 20
    
    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = Settings()
        return cls.__instance

    def __init__(self):
        if Settings.__instance is not None:
            raise Exception("Use Settings.get_instance() singleton")
        self.itemLimit = 0
        self.enableSuggested = False
        self.enableRecent = False
        self.enableRandom = False
        self.recentOnlyUnplayed = False
        self.randomOnlyUnplayed = False
        self.randomUpdateOnTimer = False
        self.randomUpdateOnLibraryUpdated = False
        self.randomUpdateOnHomeScreen = False
        self.randomTimer = 0
        self.ignoreSpecials = False
    
    def reload_addon_config(self):
        helper.set_property('service.skin.smartplaylist.widgets.ReloadSettings', 'false')
        addonConfig = helper.get_addon_config()
        if addonConfig:
            self.itemLimit = min([Settings.MAX_ITEM, max([0, int(addonConfig.getSetting("nb_item"))])])
            self.enableSuggested = addonConfig.getSetting("suggested_enable") == 'true'
            self.enableRecent = addonConfig.getSetting("recent_enable") == 'true'
            self.enableRandom = addonConfig.getSetting("random_enable") == 'true'
            self.recentOnlyUnplayed = addonConfig.getSetting("recent_unplayed") == 'true'
            self.randomOnlyUnplayed = addonConfig.getSetting("random_unplayed") == 'true'
            self.randomUpdateOnTimer = int(addonConfig.getSetting("random_method")) == 0
            self.randomUpdateOnLibraryUpdated = int(addonConfig.getSetting("random_method")) == 1
            self.randomUpdateOnHomeScreen = int(addonConfig.getSetting("random_method")) == 2
            self.randomTimer = int(float(addonConfig.getSetting("random_timer"))) if (self.enableRandom and self.randomUpdateOnTimer) else 0
            self.ignoreSpecials = addonConfig.getSetting("ignore_specials") == 'true'
    
    def is_reload_addon_config_required(self):
        return helper.get_property('service.skin.smartplaylist.widgets.ReloadSettings') != 'false'
        
    def get_enabled_modes(self):
        modes = []
        if self.enableSuggested:
            modes.append('Suggested')
        if self.enableRecent:
            modes.append('Recent')
        if self.enableRandom:
            modes.append('Random')
        return modes