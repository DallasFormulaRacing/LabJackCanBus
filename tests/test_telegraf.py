import pandas as pd
from unittest.mock import call


def test_send_linpot_metric(linpot_instance, mock_telegraf, linpot_data):
    linpot_instance.telegraf_client = mock_telegraf

    for run, run_data in linpot_data.items():
        df = pd.DataFrame([run_data])
        df['SYSTEM_TIMER_20HZ'] = 1000

        linpot_instance.send_linpot_metrics(df)

        # the expected call is how 
        expected_calls = [
            call(metric_name, value, tags={"source": "linpot"}, timestamp=1000)
            for metric_name, value in run_data.items()
        ]
        mock_telegraf.metric.assert_has_calls(expected_calls, any_order=True)

        mock_telegraf.reset_mock()


def test_send_metric():
    pass