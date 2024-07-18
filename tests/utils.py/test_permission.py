import pytest
from django.contrib.auth.models import Permission

from account.models import CustomUser
from utils.permissions import has_modify_permissions


@pytest.fixture
def user_with_permissions():
    user = CustomUser.objects.create_user(
        "testuser", "test@example.com", "password"
    )
    permission = Permission.objects.filter(
        codename="add_chat",
    ).first()
    user.user_permissions.add(permission)
    return user


@pytest.mark.django_db
@pytest.mark.parametrize(
    "app,module,expected",
    [
        ("chat", "chat", True),
        ("chat", "message", False),
    ],
)
def test_has_modify_permissions(user_with_permissions, app, module, expected):
    assert (
        has_modify_permissions(user_with_permissions, app, module) == expected
    )
