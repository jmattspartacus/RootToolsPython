
import sys


def find_in_list_items(ll, thing, require_equality: bool = False):
    if require_equality:
        for i in range(len(ll)):
            if thing == ll[i]:
                return i
    else:
        for i in range(len(ll)):
            if thing in ll[i]:
                return i
    return -1


def parse_int_arg(arglist, argname, success_message, default_value, value_delimeter = "=", kill_on_fail=True, min_value = -sys.maxsize, max_value = sys.maxsize ):
    if any([i in value_delimeter for i in [" ", "\n", "\r", "\t"]]) or len(value_delimeter) != 1:
        raise ValueError("ValueDelimiter must be a single character that is not whitespace or newline")
    argidx = find_in_list_items(arglist, argname)
    if argidx != -1:
        spl = arglist[argidx].split(value_delimeter)
        if len(spl) != 2 or len(spl[1]) == 0:
            print(f"Failed to parse argument {argname}! Syntax: {argname}{value_delimeter}2")
            if kill_on_fail:
                sys.exit(1)
            return default_value
        try:
            argnum = int(spl[1])
            if argnum < min_value:
                print(f"Bad argument value for {argname}, value given ({argnum}) is less than minimum of {min_value}")
                if kill_on_fail:
                    sys.exit(1)
                print(f"Setting to default {default_value}")
                return default_value
            elif argnum > max_value:
                print(f"Bad argument value for {argname}, value given ({argnum}) is greater than max of {max_value}")
                if kill_on_fail:
                    sys.exit(1)
                print(f"Setting to default {default_value}")
                return default_value
            else:  
                tsuccess = success_message.replace("$argval", f"{argnum}").replace("$argname", f"{argname}")
                if len(tsuccess) > 0:
                    print(tsuccess)
                return argnum
        except Exception as e:
            print(f"Threw an exception while trying to parse {argname}")
            print(e)
            if kill_on_fail:
                sys.exit(1)
            return default_value
    else:
        print(f"Using default value for {argname}{value_delimeter}{default_value}")
        return default_value


def str_to_math(thing):
    repl = [("c", "0"), ("m", "-"), ("p", "+")]
    t = thing
    for i in repl:
        t = t.replace(i[0], i[1])
    return t

def replace_from_iterable(thing, replace):
    t = thing
    for i in replace:
        t = t.replace(i[0], i[1])
    return t

def remove_from_iterable(thing, replace):
    t = thing
    for i in replace:
        t = t.replace(i[0], "")
    return t

def remove_all_from_str(obj: str, remove_me: str) -> str:
    if not isinstance(obj, str):
        raise TypeError("obj must be str")
    tstr = obj
    tobj = tstr.replace(remove_me, "")
    while(tobj != tstr):
        tstr = tobj
        tobj = tstr.replace(remove_me, "")
    return tobj

def parse_boolean(args, flag_arg: str, require_equality: bool = True, silent: bool = True, output_message: str = "$argname=$argval", only_output_on_success: bool = False) -> bool:
    if not isinstance(flag_arg, str):
        raise TypeError("flag_arg must be str!")
    ret = find_in_list_items(args, flag_arg, require_equality) != -1
    should_print = not silent
    if only_output_on_success:
        should_print = should_print and ret
    if should_print:
        msg = output_message.replace("$argname", flag_arg).replace("$argval", str(ret))
        print(msg)
    return ret


def parse_string_arg(arglist, argname, success_message, default_value="None", value_delimeter = "=", kill_on_fail=True, silent=False) -> str:
    if any([i in value_delimeter for i in [" ", "\n", "\r", "\t"]]) or len(value_delimeter) != 1:
        raise ValueError("ValueDelimiter must be a single character that is not whitespace or newline")
    argidx = find_in_list_items(arglist, argname)
    if argidx != -1:
        spl = arglist[argidx].split(value_delimeter)
        if len(spl) != 2 or len(spl[1]) == 0:
            if not silent:
                print(f"Failed to parse argument {argname}! Syntax: {argname}{value_delimeter}2")
            if kill_on_fail:
                sys.exit(1)
            return default_value
        try:
            argval = spl[1]
            tsuccess = success_message.replace("$argval", f"{argval}").replace("$argname", f"{argname}")
            if len(tsuccess) > 0 and not silent:
                print(tsuccess)
            return argval
        except Exception as e:
            if not silent:
                print(f"Threw an exception while trying to parse {argname}")
                print(e)
            if kill_on_fail:
                sys.exit(1)
            return default_value
    elif not kill_on_fail and not silent:
        print(f"Using default value for {argname}{value_delimeter}{default_value}")
        return default_value
    if kill_on_fail:
        if not silent:
            print(f"Required argument '{argname}' not found, supply this argument using {argname}{value_delimeter}value. Abort!")
        sys.exit(1)