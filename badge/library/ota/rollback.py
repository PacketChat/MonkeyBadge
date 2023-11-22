from esp32 import Partition


# Mark this boot as successful: prevent rollback to last image on next reboot.
# Raises OSError(-261) if bootloader is not OTA capable.
def cancel() -> None:
    try:
        Partition.mark_app_valid_cancel_rollback()
    except OSError as e:
        if e.args[0] == -261:
            print("The bootloader does not support OTA rollback.")
        else:
            raise e


def force() -> None:
    from .status import force_rollback

    force_rollback()


def cancel_force() -> None:
    from .status import current_ota

    current_ota.set_boot()
