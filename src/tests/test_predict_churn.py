import pytest
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to
import apache_beam as beam
from churn_prediction_pipeline.predict_churn import predict_churn
from churn_prediction_pipeline.data import internal_churn_pred_data, output_churn_pred_data
from churn_prediction_pipeline.config import config
import pandas as pd
from unittest.mock import Mock

@pytest.fixture
def pipeline():
    return TestPipeline()

def test_predict_churn(pipeline):
    # Mock the model
    class MockModel:
        def predict(self, df):
            
            total_charges = df['TotalCharges'][0]
            if total_charges == 100.0:
                predict = 1  # Simulate 'churn'
            elif total_charges == 500.0:
                predict = 0  # Simulate 'no churn'
            else:
                predict = 0  # Default prediction if unknown value
            print("Total Charges:", total_charges)
            print("Prediction:", predict)
            return predict
    mock_model = MockModel()

    # Create the instance of PredictChurn with the mock model
    predict = predict_churn(mock_model)

    input_data = [
        internal_churn_pred_data.dict_to_pydantic({
            'customerID': '12345',
            'Contract': 'One year',
            'tenure': 12,
            'PhoneService': 1,  # Assuming 'Yes' -> 1
            'TotalCharges': 100.0,
            'Month-to-month': 0,
            'One year': 1,
            'Two year': 0
        }),
        internal_churn_pred_data.dict_to_pydantic({
            'customerID': '67890',
            'Contract': 'Month-to-month',
            'tenure': 24,
            'PhoneService': 0,  # Assuming 'No' -> 0
            'TotalCharges': 500.0,
            'Month-to-month': 1,
            'One year': 0,
            'Two year': 0
        })
    ]

    expected_output = [
        output_churn_pred_data.dict_to_pydantic({
            'customerID': '12345',
            'Contract': 'One year',
            'tenure': 12,
            'PhoneService': 'Yes',
            'TotalCharges': 100.0,
            'prediction': 'churn'
        }),
        output_churn_pred_data.dict_to_pydantic({
            'customerID': '67890',
            'Contract': 'Month-to-month',
            'tenure': 24,
            'PhoneService': 'No',
            'TotalCharges': 500.0,
            'prediction': 'no churn'
        })
    ]

    mean_tenure_pcoll = pipeline | 'Create mean_tenure' >> beam.Create([12])
    
    result = (
        pipeline
        | 'Create Input' >> beam.Create(input_data)
        | 'Apply Prediction' >> beam.ParDo(predict)
    )

    # Use assert_that to check the output
    assert_that(result, equal_to(expected_output))

    pipeline.run()
