from .basic_commands import register_basic_commands
from .custom_commands import register_custom_commands
from .support_functions import register_support_functions


def register_all_handlers(dp) -> None:  # function for registration of all handlers
    handlers = (register_custom_commands, register_basic_commands, register_support_functions)

    for handler in handlers:
        handler(dp)


