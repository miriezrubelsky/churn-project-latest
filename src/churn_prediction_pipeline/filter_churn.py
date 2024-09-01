import logging
from pydantic import ValidationError
from churn_prediction_pipeline.data import churn_pred_data
import apache_beam as beam
from churn_prediction_pipeline.config import config

# Setting up logging
logging.basicConfig(
    filename=config.LOGGING_FILENAME,
    filemode=config.LOGGING_FILEMODE,
    level=getattr(logging, config.LOGGING_LEVEL),  # Convert string level to logging constant
    format=config.LOGGING_FORMAT
)
logger = logging.getLogger(__name__)

def __init__(self):
     logger.debug("filter churn constructor ")   

class filter_churn(beam.DoFn):
    def process(self, row):
        customerId = row['customerID']
        try:
            # Convert string values to appropriate types before passing to Pydantic model
            if 'TotalCharges' in row:
                row['TotalCharges'] = float(row['TotalCharges']) if row['TotalCharges'].strip() else None
            if 'tenure' in row:
                row['tenure'] = int(round(float(row['tenure']))) if row['tenure'].strip() else None
            
            # Convert row dictionary to Pydantic model
            churn_pred = churn_pred_data.dict_to_pydantic(row)
            logger.debug("Row after filtering: %s", churn_pred)
            yield churn_pred
        
        except (ValueError, ValidationError) as e:
            logger.debug("Validation error: %s for customerID: %s", e, customerId)
            yield None
