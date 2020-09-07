from canoser import Struct, Uint64
from lbrtypes.on_chain_config import OnChainConfig

class LibraVersion(Struct, OnChainConfig):
    IDENTIFIER = "LibraVersion"
    _fields = [
        ("major", Uint64)
    ]