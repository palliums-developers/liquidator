from move_core_types.language_storage import ModuleId, StructTag, CORE_CODE_ADDRESS

ACCOUNT_MODULE_NAME = "LibraAccount"

# Account
ACCOUNT_MODULE_IDENTIFIER = "LibraAccount"

#/ The ModuleId for the Account module.
ACCOUNT_MODULE = ModuleId(CORE_CODE_ADDRESS, ACCOUNT_MODULE_IDENTIFIER)

# Payment Events
SENT_EVENT_NAME = "SentPaymentEvent"
RECEIVED_EVENT_NAME = "ReceivedPaymentEvent"

def sent_event_name():
    return SENT_EVENT_NAME

def received_event_name():
    return RECEIVED_EVENT_NAME
