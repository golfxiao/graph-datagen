from typing import Dict
from faker.providers import BaseProvider
from datagen import log


def argparse(argstr):
    arg = int(argstr)
    if arg > 0:
        return (arg,)
    else:
        raise Exception(f"Invalid argument:{argstr}, expect an integer greater than 0.")


class Provider(BaseProvider):
    """Stateful auto-increment sequence generators.
    You should call _reset method to clean up the state if you want to reuse it"""

    __provider__ = "sequence_provider"

    def __init__(self, *args):
        super().__init__(*args)
        self._offsets: Dict[str, int] = {}

    def id(self, tag: str = "default", start=0, max=None, prefix=None) -> int:
        if tag not in self._offsets:
            self._offsets[tag] = 0

        seq = start + self._offsets[tag]
        if max and seq >= max:
            self._offsets[tag] = 0
            seq = start

        self._offsets[tag] += 1
        if prefix and len(prefix) > 0:
            return f"{prefix}{seq}"
        else:
            return seq

    def _reset(self, tag=None):
        """Clean up the state of the provider."""
        if tag is None:
            self._offsets.clear()
        else:
            del self._offsets[tag]
        log.info(f"Reset state for sequence provider, tag: {tag}")
