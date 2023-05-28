from faker.providers import BaseProvider


def argparse(argstr):
    if argstr:
        return (argstr,)
    else:
        raise Exception(f"Invalid argument, unexpected empty string of eval rule args.")


class Provider(BaseProvider):
    def __init__(self, generator):
        super().__init__(generator)

    def eval(self, expr, **kwargs):
        return eval(expr, None, kwargs)
