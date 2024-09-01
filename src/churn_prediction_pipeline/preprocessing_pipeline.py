# Combine the Transformers into a Pipeline
from sklearn.pipeline import Pipeline
import pandas as pd
from churn_prediction_pipeline.data import churn_pred_data, internal_churn_pred_data
from churn_prediction_pipeline.processing import preprocessing as pp 
from churn_prediction_pipeline.config import config
import apache_beam as beam
import logging

logging.basicConfig(
    filename=config.LOGGING_FILENAME,
    filemode=config.LOGGING_FILEMODE,
    level=getattr(logging, config.LOGGING_LEVEL),  # Convert string level to logging constant
    format=config.LOGGING_FORMAT
)
logger = logging.getLogger(__name__)

class preprocessing_pipeline(beam.DoFn):
    def __init__(self):
        self.pipeline = None
    
    def process(self, element, mean_tenure):
        self.pipeline = Pipeline([
            ('fill_phone_service', pp.FillMissingPhoneService()),
            ('map_phone_service', pp.MapPhoneService()),
            ('impute_tenure', pp.ImputeTenure(tenure_mean=mean_tenure)),
            ('impute_total_charges', pp.ImputeTotalCharges(total_charges_mean=2279)),
            ('one_hot_encode_contract', pp.OneHotEncodeContract()),
        #    ('create_internal_churn_pred', pp.CreateInternalChurnPred()),
        ])
        
        data = churn_pred_data.pydantic_to_dict(element)
         # Convert the input element to a DataFrame
        df = pd.DataFrame([data], columns=config.pre_processing_columns)
        logger.debug("data to process: %s ",df)
        
        transformed_df = self.pipeline.transform(df)
         # Convert the DataFrame back to a dictionary or other required format
        result = transformed_df.to_dict(orient='records')[0]
        logger.debug("Row to preprocess %s ",result)
        #print("Row to preprocess", transformed_df)
        internal_data = internal_churn_pred_data.dict_to_pydantic({
            'customerID': result.get('customerID'),
            'Contract': result.get('Contract'),
            'tenure': result.get('tenure'),
            'PhoneService': result.get('PhoneService'),
            'TotalCharges': result.get('TotalCharges'),
            'Month-to-month': result.get('Contract_Month-to-month', 0),
            'One year': result.get('Contract_One year', 0),
            'Two year': result.get('Contract_Two year', 0)
        })
        logger.debug("Internal Churn: %s for",internal_churn_pred_data)
       # print("Internal Churn", internal_churn_pred_data)
        yield internal_data

