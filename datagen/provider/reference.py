from faker.providers import BaseProvider
from datagen import log


def argparse(argstr):
    if argstr:
        return (argstr,)
    else:
        raise Exception(
            f"Invalid argument, unexpected empty string of oftag rule args."
        )


class Provider(BaseProvider):
    """Variable placeholders in pattern, which only support normal variable identifiers
    such as letters, numbers, and underscores."""

    def __init__(self, generator):
        super().__init__(generator)

    def reference(self, pattern, **kwargs):
        return pattern.format(**kwargs)
