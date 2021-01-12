from os import stat
from ujson import dumps, loads
from hw import log

def load_json(json):
    log.info("Load json: %s", json)
    try:
        with open(json) as fp:
            data = loads(fp.read())
            if type(data) == str:
                if data == "[]":
                    return []
                return {}
        log.info("Read json, done")
        return data
    except BaseException as e: #NOSONAR
        log.error("Read json failed! %s", e)
    return None

def dump_json(obj, file):
    log.info("Write json to file as string: %s", file)
    try:
        with open(file, "w") as fp:
            fp.write(dumps(obj))
        log.info("Write json, done")
        return True
    except BaseException as e: #NOSONAR
        log.error("Write json failed! %s", e)
    return False

def file_exists(f):
    try:
        stat(f)
        return True
    except: #NOSONAR #pylint: disable=bare-except
        return False
