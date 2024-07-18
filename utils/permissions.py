from typing import Callable

from account.models import CustomUser


def has_modify_permissions(user: CustomUser, app: str, module: str) -> bool:
    """
    Checks if a user has permissions to change or
    add items in a specific module.

    :param user: The user whose permissions are being checked.
    :param module: The module for which the permissions are being checked.
    :return: True if the user has permissions to change or
        add items in the specified module, False otherwise.
    """
    return user.has_perm(f"{app}.change_{module}") or user.has_perm(
        f"{app}.add_{module}"
    )


def has_modify_permissions_for_module(
    app: str, module: str
) -> Callable[[CustomUser], bool]:
    """
    Creates a permission-checking function for a specific module.

    :param module: The module for which the permissions are
        being checked.
    :return: Returns True if the user has permissions to change
        or add items in the specified module, False otherwise.
    """

    def has_permissions(user: CustomUser) -> bool:
        """
        Checks if the user has permissions to change
        or add items in the specified module.

        :param user: The user whose permissions are being checked.
        :return: True if the user has permissions to change or
            add items in the specified module, False otherwise.
        """
        return has_modify_permissions(user, app, module)

    return has_permissions
