import logging
import pytest

# Configure logging at the top of the file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)
@pytest.mark.flaky(reruns=5)
@pytest.mark.usefixtures("appium_driver", "log_on_failure")
class BaseTest:
    pass