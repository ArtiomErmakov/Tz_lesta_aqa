import logging

from typing import List, Union, NoReturn


def raise_assert(msg: Union[str, List[str]]) -> NoReturn:
    if isinstance(msg, list):
        msg = str(msg)
    logging.info(msg)
    raise AssertionError(msg)
