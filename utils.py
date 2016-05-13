''' utils module
    for functions of general use and utility'''


def on_cluster():
    import platform
    import re
    uname = platform.uname()
    pattern = re.compile("^(leftraru\d)|(cn\d\d\d)")
    return bool(pattern.match(uname[1]))


def trymkdir(path):
    ''' mkdir if path does not exist yet '''
    import os
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
