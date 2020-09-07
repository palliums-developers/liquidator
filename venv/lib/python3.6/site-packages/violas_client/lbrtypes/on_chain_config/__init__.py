from .mod import *
from .libra_version import LibraVersion
from .validator_set import ValidatorSet
from .registered_currencies import RegisteredCurrencies
from .dual_attestation_limit import DualAttestationLimit
from .vm_config import VMConfig
ON_CHAIN_CONFIG_REGISTRY = [VMConfig, LibraVersion, ValidatorSet, RegisteredCurrencies, DualAttestationLimit]


