import logconf


class ShareLogger:
    logger = logconf.initLogger('log.txt', True, True)


def getShareLogger():
    return ShareLogger.logger


def setShareLogger(logger):
    ShareLogger.logger = logger