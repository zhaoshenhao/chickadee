from ujson import dumps, loads
from hw import log
from os import stat

'''
Load data from json file
'''
def load_json(json):
    log.info("Load json: %s", json)
    try:
        with open(json) as fp:
            data = loads(fp.read())
            if type(data) == str:
                if data == "[]":
                    return []
                else:
                    return {}
        log.info("Read json, done")
        return data
    except Exception as e:
        log.error("Read json failed! %s", e)
    return None

'''
Save data to json file
'''
def dump_json(obj, file):
    log.info("Write json to file as string: %s", file)
    try:
        with open(file, "w") as fp:
            fp.write(dumps(obj))
        log.info("Write json, done")
        return True
    except Exception as e:
        log.error("Write json failed! %s", e)
    return False

'''
Check file existence
'''
def file_exists(f):
    try:
        stat(f)
        return True
    except Exception as e: #NOSONAR
        return False
