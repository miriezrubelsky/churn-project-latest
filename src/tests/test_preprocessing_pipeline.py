import pytest
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to
import apache_beam as beam
from churn_prediction_pipeline.preprocessing_pipeline import preprocessing_pipeline
from churn_prediction_pipeline.data import churn_pred_data, internal_churn_pred_data
from churn_prediction_pipeline.config import config



@pytest.fixture
def pipeline():
    return TestPipeline()

def test_preprocessing_pipeline(pipeline):
    input_data = [
        churn_pred_data.dict_to_pydantic({'customerID':'001', 'tenure':1, 'PhoneService':'Yes', 'Contract':'Month-to-month', 'TotalCharges':29.85}),
        churn_pred_data.dict_to_pydantic({'customerID':'002', 'tenure':34, 'PhoneService':'No', 'Contract':'One year', 'TotalCharges':1889.5})

    ]
    
    expected_output = [
        internal_churn_pred_data.dict_to_pydantic({
            'customerID': '001',
            'Contract':'Month-to-month',
            'tenure': 1,
            'PhoneService': 1,  # Assuming 'Yes' -> 1 in the transformation
            'TotalCharges': 29.85,
            'Month-to-month': 1,
            'One year': 0,
            'Two year': 0
            
        }),
        internal_churn_pred_data.dict_to_pydantic({
            'customerID': '002',
            'Contract':'One year',
            'tenure': 34,
            'PhoneService': 0,  # Assuming 'No' -> 0 in the transformation
            'TotalCharges': 1889.5,
            'Month-to-month': 0,
            'One year': 1,
            'Two year': 0
          
        })
    ]

    mean_tenure_pcoll = pipeline | 'Create mean_tenure' >> beam.Create([12])
    
    result = (
        pipeline
        | 'Create Input' >> beam.Create(input_data)
        | 'Apply Pipeline' >> beam.ParDo(preprocessing_pipeline(), mean_tenure=beam.pvalue.AsSingleton(mean_tenure_pcoll))
    )
    
    # Use assert_that to check the output
    assert_that(result, equal_to(expected_output))

    pipeline.run()
