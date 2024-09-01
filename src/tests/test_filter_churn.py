import pytest
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to
import apache_beam as beam
from churn_prediction_pipeline.filter_churn import filter_churn
from churn_prediction_pipeline.data import churn_pred_data, internal_churn_pred_data
from churn_prediction_pipeline.config import config

@pytest.fixture
def pipeline():
    return TestPipeline()

def test_filter_churn(pipeline):
    # Create the instance of filter_churn
    filter_churn_instance = filter_churn()

    input_data = [
        {
            'customerID': '12345',
            'TotalCharges': '100.0',
            'tenure': '12',
            'PhoneService': 'Yes',
            'Contract': 'One year'
        },
        {
            'customerID': '67890',
            'TotalCharges': '500.0',
            'tenure': '24',
            'PhoneService': 'No',
            'Contract': 'Month-to-month'
        }
    ]

    expected_output = [
        churn_pred_data.dict_to_pydantic({
            'customerID': '12345',
            'Contract': 'One year',
            'tenure': 12,
            'PhoneService': 'Yes',
            'TotalCharges': 100.0,
            'Month-to-month': 0,
            'One year': 1,
            'Two year': 0
        }),
        churn_pred_data.dict_to_pydantic({
            'customerID': '67890',
            'Contract': 'Month-to-month',
            'tenure': 24,
            'PhoneService': 'No',
            'TotalCharges': 500.0,
            'Month-to-month': 1,
            'One year': 0,
            'Two year': 0
        })
    ]

    result = (
        pipeline
        | 'Create Input' >> beam.Create(input_data)
        | 'Apply Filter Churn' >> beam.ParDo(filter_churn_instance)
    )

    # Use assert_that to check the output
    assert_that(result, equal_to(expected_output))

    pipeline.run()
