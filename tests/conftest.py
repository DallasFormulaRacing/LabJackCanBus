import pytest
from unittest.mock import patch
from sensors.AnalogStream import Linpot


@pytest.fixture
def linpot_data():
  import json
  with open('tests/models.json') as f:
    data = json.load(f)
    return data['linpot']


@pytest.fixture
def linpot_instance():
  return Linpot()


@pytest.fixture
def mock_telegraf():
    with patch('telegraf.client.TelegrafClient') as mock_telegraf:
        yield mock_telegraf
