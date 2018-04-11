from enum import Enum
from hashlib import md5


class FetchType(Enum):
    Image = 1
    Page = 2
    CustomContent = 3


def mymd5(mystr):
    m = md5()
    m.update(mystr.encode())
    return m.hexdigest()