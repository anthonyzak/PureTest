from chat.providers import BaseProvider, SlingAcademyProvider


class ProviderFactory:
    """
    Factory class for creating instances of BaseProvider
    based on provider_name.
    """

    @staticmethod
    def get_provider(provider_name: str) -> BaseProvider:
        """
        Return an instance of BaseProvider based on the provider_name.

        :param provider_name: The name of the provider to fetch data from.
        :return: Instance of the corresponding provider.
        :raises ValueError: If the provider_name is not supported.
        """
        if provider_name.lower() == "sling_academy":
            return SlingAcademyProvider()
        else:
            raise ValueError(f"Provider not support: {provider_name}")
