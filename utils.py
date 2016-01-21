''' utils module
    for functions of general use and utility'''


def trymkdir(path):
    ''' mkdir if path does not exist yet '''
    import os
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
