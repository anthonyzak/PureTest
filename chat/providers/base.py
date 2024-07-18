from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseProvider(ABC):
    """
    Abstract base class for data providers.
    """

    @abstractmethod
    def fetch_data(self) -> Dict[str, Any]:
        """
        Fetch data from the provider.

        :return: Dictionary containing the fetched data.
        """

    @abstractmethod
    def process_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process the fetched data.

        :param data: Dictionary containing the fetched data.
        :return: List of dictionaries containing processed data.
        """

    @abstractmethod
    def save_data(self, processed_data: List[Dict[str, Any]]) -> None:
        """
        Save processed data.

        :param processed_data: List of dictionaries containing processed data.
        :return: None
        """
