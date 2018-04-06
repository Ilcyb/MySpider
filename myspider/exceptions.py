class SpiderError(Exception):
    pass


class SaveCookiesError(SpiderError):
    """A save cookie error occurred"""
    pass


class LoadCookiesError(SpiderError):
    """A load cookie error occureed"""
    pass