import random
import uuid
from typing import Any, List

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from account.models import CustomUser
from chat.models import Chat


class Command(BaseCommand):
    """
    Django management command to generate thousands of
    chats distributed among multiple users.
    """

    help = (
        "Generates thousands of chats in the database distributed "
        "among multiple users"
    )

    def add_arguments(self, parser) -> None:
        """
        Add command line arguments to the parser.

        :param parser: The argument parser.
        """
        parser.add_argument(
            "num_chats", type=int, help="Number of chats to create"
        )
        parser.add_argument(
            "--num_users",
            type=int,
            default=5,
            help="Number of users to create (default: 5)",
        )

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """
        Handle the execution of the command.

        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        num_chats = kwargs["num_chats"]
        num_users = kwargs["num_users"]

        self.stdout.write(self.style.SUCCESS(f"Creating {num_users} users..."))
        users = self.create_users(num_users)

        self.stdout.write(self.style.SUCCESS(f"Creating {num_chats} chats..."))
        self.create_chats(num_chats, users)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {num_chats} chats for {num_users} users"
            )
        )

    def create_users(self, num_users: int) -> List[CustomUser]:
        """
        Create a specified number of users.

        :param num_users: Number of users to create.
        :return: List of created CustomUser instances.
        """
        users_to_create = []
        for i in range(num_users):
            username = f"testuser_{i}_{uuid.uuid4().hex[:8]}"
            user = CustomUser(
                username=username, password=make_password("testpassword")
            )
            users_to_create.append(user)

        users = CustomUser.objects.bulk_create(users_to_create, batch_size=500)
        return users

    def create_chats(self, num_chats: int, users: List[CustomUser]) -> None:
        """
        Create a specified number of chats assigned to random users.

        :param num_chats: Number of chats to create.
        :param users: List of users among whom the chats will be distributed.
        """
        chats_to_create = []
        for _ in range(num_chats):
            user = random.choice(users)  # nosec B311
            chat = Chat(user=user)
            chats_to_create.append(chat)

        Chat.objects.bulk_create(chats_to_create, batch_size=500)
