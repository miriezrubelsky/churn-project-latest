from pydantic import BaseModel, conint, Field
from typing import Optional
from enum import Enum

# Define the Enums
class ContractEnum(str, Enum):
    month_to_month = 'Month-to-month'
    one_year = 'One year'
    two_year = 'Two year'

# Define the Pydantic BaseModel
class internal_churn_pred_data(BaseModel):
    customerID: str
    Contract: ContractEnum
    tenure: int
    PhoneService: conint(ge=0, le=1)
    TotalCharges: float
    Month_to_month: conint(ge=0, le=1) = Field(..., alias='Month-to-month')
    One_year: conint(ge=0, le=1) = Field(..., alias='One year')
    Two_year: conint(ge=0, le=1) = Field(..., alias='Two year')
    

# Function to convert Pydantic model to dictionary
def pydantic_to_dict(model: internal_churn_pred_data) -> dict:
    return model.dict(by_alias=True)

# Function to convert dictionary back to Pydantic model
def dict_to_pydantic(data: dict) -> internal_churn_pred_data:
    return internal_churn_pred_data(**data)

# Example Usage

# Create a Pydantic model
# pydantic_internal_churn_pred = InternalChurnPred(
#     customerID="12345",
#     Contract=ContractEnum.one_year,
#     tenure=12,
#     PhoneService=1,
#     TotalCharges=500.0,
#     Month_to_month=0,
#     One_year=1,
#     Two_year=0,
#     prediction=1
# )

# # Convert Pydantic model to dictionary
# internal_churn_pred_dict = pydantic_to_dict(pydantic_internal_churn_pred)
# print("Dictionary:", internal_churn_pred_dict)

# # Convert dictionary back to Pydantic model
# new_pydantic_internal_churn_pred = dict_to_pydantic(internal_churn_pred_dict)
# print("Pydantic Model:", new_pydantic_internal_churn_pred)
