import playlist as pl

class AudioPlaylist(pl.Playlist):
    def __init__(self, alias, path, name, type, itemType):
        pl.Playlist.__init__(self, alias, path, name, type, itemType, 'music')
        