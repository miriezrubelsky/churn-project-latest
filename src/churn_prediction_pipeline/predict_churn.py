from churn_prediction_pipeline.data import output_churn_pred_data
from churn_prediction_pipeline.config import config
import apache_beam as beam
import pandas as pd
import logging

logging.basicConfig(
    filename=config.LOGGING_FILENAME,
    filemode=config.LOGGING_FILEMODE,
    level=getattr(logging, config.LOGGING_LEVEL),  # Convert string level to logging constant
    format=config.LOGGING_FORMAT
)
logger = logging.getLogger(__name__)

class predict_churn(beam.DoFn):
    def __init__(self, model):
        self.model = model

    def process(self, internal_churn_pred_data):

        alias_to_attr_map = {
            'Month-to-month': 'Month_to_month',
            'One year': 'One_year',
            'Two year': 'Two_year'
        }

        
        features = [getattr(internal_churn_pred_data, alias_to_attr_map.get(column, column)) for column in config.result_columns]
        df = pd.DataFrame([features], columns=config.result_columns)
        logger.debug("Row to Predict %s ",df)
      #  print("Row to Predict", df)
        prediction = self.model.predict(df)
        output_data = output_churn_pred_data.dict_to_pydantic({
            'customerID': getattr(internal_churn_pred_data,'customerID'),
            'Contract':getattr(internal_churn_pred_data,'Contract'),
            'tenure': getattr(internal_churn_pred_data,'tenure') ,
            'PhoneService': 'Yes' if getattr(internal_churn_pred_data, 'PhoneService') == 1 else 'No',
            'TotalCharges': getattr(internal_churn_pred_data,'TotalCharges'),
            'prediction': 'churn' if prediction == 1 else 'no churn'
          
        })
       # internalChurnPred.prediction = prediction[0]
        logger.debug("Row with prediction: %s ",output_data)
    #    print("Row with prediction", output_data)
        yield output_data    
