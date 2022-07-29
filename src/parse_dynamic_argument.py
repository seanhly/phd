from arguments import Argument


def parse_dynamic_argument(argument: str, action: str):
    for T in Argument.__subclasses__():
        if T.fits(argument):
            return T(argument, action)
    return None
