from celery import shared_task
from celery.utils.log import get_task_logger

from chat.providers import ProviderFactory

logger = get_task_logger(__name__)


@shared_task
def fetch_photos_from_api(provider_name: str) -> None:
    """
    Fetches photos from the specified provider API
    and saves them to the database.

    :param provider_name: The name of the provider to fetch data from.
    :return: None
    :raises Exception: If there is an error during the fetch or save process.
    """
    try:
        provider = ProviderFactory.get_provider(provider_name)
        data = provider.fetch_data()
        processed_data = provider.process_data(data)
        provider.save_data(processed_data)
        logger.info(
            f"Successfully fetched and saved {len(processed_data)}"
            f"new images from {provider_name}"
        )
    except Exception as e:
        logger.error(f"Error fetching photos from {provider_name}: {str(e)}")
