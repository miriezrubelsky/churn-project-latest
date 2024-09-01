from typing import Optional
from enum import Enum
from pydantic import BaseModel

class ContractEnum(str, Enum):
    month_to_month = 'Month-to-month'
    one_year = 'One year'
    two_year = 'Two year'

class PhoneServiceEnum(str, Enum):
    yes = 'Yes'
    no = 'No'

class PredictionEnum(str, Enum):
    churn = 'churn'
    no_churn = 'no churn'    

# Define the Pydantic BaseModel
class output_churn_pred_data(BaseModel):
    customerID: str
    TotalCharges: float 
    Contract: ContractEnum
    PhoneService: PhoneServiceEnum
    tenure: int 
    prediction: PredictionEnum

def pydantic_to_dict(model: output_churn_pred_data) -> dict:
    return model.dict(by_alias=True)

# Function to convert dictionary back to Pydantic model
def dict_to_pydantic(data: dict) -> output_churn_pred_data:
    return output_churn_pred_data(**data)    