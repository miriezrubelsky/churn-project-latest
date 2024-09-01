from churn_prediction_pipeline.config import config
import pickle
import os

def load_churn_model():
    model_path = os.path.join(config.SAVE_MODEL_PATH,config.MODEL_NAME)
    with open(model_path, 'rb') as f:
         rf_model = pickle.load(f)
    return    rf_model  