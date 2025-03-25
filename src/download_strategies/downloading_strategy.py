from abc import ABC, abstractmethod
from src.utils.media_object_class import MediaObject

class DownloadingStrategy(ABC):
    """
    Abstract base class defining the interface for all concrete download strategies.
    Concrete implementations must override the `download` method and can optionally
    customize the `timeout` property.

    Attributes:
    -----------
    timeout (int): 
        Maximum time (in seconds) allowed for a download operation.
        Defaults to 30 seconds. Can be overridden by subclasses.

    strategy_settings (dict):
        A dictionary holding the settings for the downloading strategy, allowing flexible
        configuration for different strategies such as bitrate, chunk size, etc.

    Methods:
    --------
    download():
        Abstract method that must be implemented by any subclass. 
        Defines how the downloading should be performed for each strategy.
    """

    @property
    @abstractmethod
    def timeout(self) -> int:
        """The maximum duration (in seconds) before a download is aborted."""
        return 30  # Default value (can be overridden)

    @abstractmethod
    def download(self, video: MediaObject):
        """
        Abstract method to download a video from the passed instance.
        This method should define the actual downloading process for the 
        specific downloading strategy.

        Raises:
        -------
        NotImplementedError:
            If the method is not implemented in a subclass.

        """
        raise NotImplementedError("Concrete strategies must implement this method.")