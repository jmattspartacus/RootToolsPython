from typing import Tuple
import json
import numpy




def is_json_serializable(obj) -> bool:
    typehandlers = {
        numpy.ndarray: lambda obj: json.dumps(obj),
        Tuple: lambda obj: json.dumps(list(obj))
    }
    try:           
        if type(obj) in typehandlers:
            typehandlers[type(obj)](obj)
            return True
        else:
            json.dumps(obj)
            return True
    except:
        return False

def json_walk_dict(obj) -> dict:
    outdict = {}
    for i in obj.keys():
        val = obj[i]
        # all keys must be strings for json to like it
        tkey = str(i)
        if isinstance(val, dict):
            outdict[tkey] = json_walk_dict(val)
        elif is_json_serializable(val):
            outdict[tkey] = val
    return outdict
    
def json_serialize(obj, **kwargs) -> str:
    if isinstance(obj, dict):
        outdict = json_walk_dict(obj)
        return json.dumps(outdict, **kwargs)
    elif isinstance(obj, numpy.ndarray):
        return json.dumps(obj.tolist())
    elif is_json_serializable(obj):
        return json.dumps(obj)
    else:
        return ""

def save_as_json(obj, filepath, **kwargs):
    try:
        out = json_serialize(obj, **kwargs)
    except:
        return
    with open(filepath, 'w+') as fp:
        fp.write(out)


def load_from_json(fpath, **kwargs):
    with open(fpath, "r") as fp:
        lines = "".join(fp.readlines())
    return json.loads(lines, **kwargs)