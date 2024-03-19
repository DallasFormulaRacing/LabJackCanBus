from telegraf.telegraf import Telegraf
import pytest

@pytest.fixture
def telegraf_client():
    telegraf = Telegraf()
    return telegraf