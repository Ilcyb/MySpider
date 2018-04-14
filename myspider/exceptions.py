class SpiderError(Exception):
    pass


class SaveCookiesError(SpiderError):
    """A save cookie error occurred"""
    pass


class LoadCookiesError(SpiderError):
    """A load cookie error occurred"""
    pass


class NotDirectoryError(SpiderError):
    """A not directory error occurred"""
    pass

class DirectoryNotExistsError(SpiderError):
    """A directory not exists error occurred"""
    pass
