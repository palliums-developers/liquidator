from move_core_types.language_storage import ModuleId, CORE_CODE_ADDRESS, StructTag

EVENT_MODULE_NAME = "Event"
EVENT_MODULE = ModuleId(CORE_CODE_ADDRESS, EVENT_MODULE_NAME)

EVENT_HANDLE_STRUCT_NAME = "EventHandle"
EVENT_HANDLE_GENERATOR_STRUCT_NAME = "EventHandleGenerator"

def event_module_name():
    return EVENT_MODULE_NAME

def event_handle_generator_struct_name():
    return EVENT_HANDLE_GENERATOR_STRUCT_NAME

def event_handle_struct_name():
    return EVENT_HANDLE_STRUCT_NAME

def event_handle_generator_struct_tag() -> StructTag:
    return StructTag(
        CORE_CODE_ADDRESS,
        event_module_name(),
        event_handle_generator_struct_name(),
        [],
    )