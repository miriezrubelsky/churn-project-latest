from sklearn.base import BaseEstimator, TransformerMixin

import numpy as np
import pandas as pd

class FillMissingPhoneService(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        # Fill 'PhoneService' with 'No' if it is missing
        X['PhoneService'] = X['PhoneService'].fillna('No')
        return X

class MapPhoneService(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        # Map 'PhoneService' values to numeric (1 for 'Yes', 0 for 'No')
        phone_service_mapping = {'Yes': 1, 'No': 0}
        X['PhoneService'] = X['PhoneService'].map(phone_service_mapping).fillna(0).astype(int)
        return X

class ImputeTenure(BaseEstimator, TransformerMixin):
    def __init__(self, tenure_mean):
        self.tenure_mean = tenure_mean
    
    def fit(self, X, y=None):
        return self
    
    def process_value(self,x):
        
       
        if pd.isna(x) or x == '':
            # Handle empty or NaN values by returning tenure_mean
            return self.tenure_mean
        
        try:
            return int(round(float(x)))
        except (ValueError, TypeError):
            # Handle values that cannot be converted
            print(f"Invalid tenure value: {x}, using mean value {self.tenure_mean}")
            return self.tenure_mean
          
    def transform(self, X):
        
        X = X.copy()
        X['tenure'] = X['tenure'].apply(self.process_value)
        return X

class ImputeTotalCharges(BaseEstimator, TransformerMixin):
    def __init__(self, total_charges_mean=2279):
        self.total_charges_mean = total_charges_mean
    
    def fit(self, X, y=None):
        return self
    
    def process_value(self, x):
       
        if pd.isna(x) or x == '':
            # Handle empty or NaN values by returning total_charges_mean
            return self.total_charges_mean
        
        try:
            return float(x)
        except (ValueError, TypeError):
            # Handle values that cannot be converted
            print(f"Invalid TotalCharges value: {x}, using mean value {self.total_charges_mean}")
            return self.total_charges_mean

    
    def transform(self, X):
        X = X.copy()
        # Fill missing 'TotalCharges' with the mean value
        X['TotalCharges'] = X['TotalCharges'].apply(self.process_value)
        return X

class OneHotEncodeContract(BaseEstimator, TransformerMixin):
    def __init__(self, contract_types=None):
        if contract_types is None:
            self.contract_types = ['Month-to-month', 'One year', 'Two year']
        else:
            self.contract_types = contract_types
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        if hasattr(X['Contract'].iloc[0], 'value'):
            X['Contract'] = X['Contract'].apply(lambda x: x.value)
        else:
            X['Contract'] = X['Contract'].astype(str)
        # One-hot encode the 'Contract' field
        dummies = pd.get_dummies(X['Contract'], prefix='Contract').astype(int)
        print("Unique values in 'Contract':\n", X['Contract'].unique())
    
        # Print the column names of dummies DataFrame
        print("Column names in dummies:\n", dummies.columns)
        # Ensure all contract types are present
        for contract_type in self.contract_types:
            if f'Contract_{contract_type}' not in dummies.columns:
                dummies[f'Contract_{contract_type}'] = 0
        
        X = X.join(dummies)
        return X

class CreateInternalChurnPred(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        X['Month-to-month'] = X['Contract_Month-to-month']
        X['One year'] = X['Contract_One year']
        X['Two year'] = X['Contract_Two year']
        
        return X[['customerID', 'Contract', 'tenure', 'PhoneService', 'TotalCharges', 
                  'Month-to-month', 'One year', 'Two year']]


