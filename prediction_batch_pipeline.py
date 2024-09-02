# Importing Dependencies
import sys
import os
import glob

# Add the src directory to the system path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.append(src_path)

import logging
import apache_beam as beam
import argparse
import pandas as pd
from typing import Optional
from enum import Enum
from churn_prediction_pipeline.config import config
from churn_prediction_pipeline.data import churn_pred_data
from churn_prediction_pipeline.processing import data_handling
from sklearn.pipeline import Pipeline
from churn_prediction_pipeline.processing import preprocessing as pp 
from churn_prediction_pipeline.preprocessing_pipeline import preprocessing_pipeline
from churn_prediction_pipeline.predict_churn import predict_churn
from churn_prediction_pipeline.filter_churn import filter_churn
from prometheus_client import start_http_server, Counter, Gauge
# import threading
# import time

import os
logging.basicConfig(
    filename=config.LOGGING_FILENAME,
    filemode=config.LOGGING_FILEMODE,
    level=getattr(logging, config.LOGGING_LEVEL),  # Convert string level to logging constant
    format=config.LOGGING_FORMAT
)
logger = logging.getLogger(__name__)

rf_model=data_handling.load_churn_model()

rows_processed = Counter('rows_processed', 'Number of rows processed')
rows_valid = Counter('rows_valid', 'Number of valid rows')
rows_invalid = Counter('rows_invalid', 'Number of invalid rows')
rows_empty = Counter('rows_empty', 'Number of empty rows')
mean_tenure_gauge = Gauge('mean_tenure', 'Mean tenure of the customers')



def check_file_not_empty(count):
    if count == 0:
        raise ValueError("Input file is empty")
    return count

def validate_header(header_line):
    header_columns = header_line.split(",")
    required_columns = config.schema['columns']
    # Check if all required columns are present
    missing_columns = [col for col in required_columns if col not in header_columns]
    if missing_columns:
        raise ValueError(f"Missing columns in the input file: {missing_columns}")
    return header_columns  # Return the header columns if validation is successful

class RemoveHeaderFn(beam.DoFn):
    def __init__(self, header):
        self.header = header

    def process(self, element):
        if element != self.header:
            yield element

def is_file_empty(count):
     return count > 0


def extract_tenure(row):
    tenure_str = row.get('tenure', '')
    try:
        tenure_value = float(tenure_str)
    except ValueError:
          tenure_value = 0
    
    return tenure_value

def create_non_empty_pcollection(elements, count):
            if count > 0:
                return elements
            return beam.Create([]) 


def compute_mean_tenure(pcollection):
    # Extract 'tenure' values and compute mean
    return (
        pcollection
        | "Extract Tenure" >> beam.Map(extract_tenure)
        | "Compute Mean" >> beam.CombineGlobally(beam.combiners.MeanCombineFn())
    )
   
def parse_lines(line,header):
    values = line.split(',')  # Split the line by comma
    data = dict(zip(header, values))
    rows_processed.inc() 
    return data

class ExtractHeader(beam.DoFn):
    def __init__(self):
        self.header_extracted = False

    def process(self, element):
        if not self.header_extracted:
            self.header_extracted = True
            yield element

 
def format_output_row(output_churn_pred_data):
    formatted_fields = []
    for col in config.output_columns:
        # Get the value of the attribute
        value = getattr(output_churn_pred_data, col)
            # If the value is an Enum, convert it to its string representation
        if isinstance(value, Enum):
            value = value.name
        # Append the formatted value to the list
        formatted_fields.append(str(value))
    return ','.join(formatted_fields)

   
def run(argv =None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    args,beams_args = parser.parse_known_args(argv) 

     # Check if the input path is a directory and if it is empty
    if os.path.isdir(args.input):
        # List all CSV files in the directory
        input_files = glob.glob(os.path.join(args.input, '*.csv'))
        if not input_files:
            print("The input directory is empty. Please provide a directory with data files.")
            return
    else:
        # If it's a file, treat it as a single input file
        input_files = [args.input]
  

    with beam.Pipeline(argv=beams_args) as pipe:
        config.headers = (
            pipe
            | 'Read CSV' >> beam.io.ReadFromText(input_files[0])
            | 'Extract Header' >> beam.ParDo(ExtractHeader())
            | 'Validate Header' >> beam.Map(validate_header)
          
        )

        lines = (
            pipe
            | "Read Data" >> beam.io.ReadFromText(args.input, skip_header_lines=1)
        )

        row_count = (
            lines
            | "Count Rows" >> beam.combiners.Count.Globally()
        )

        # Filter to continue processing only if the file is not empty
        non_empty_lines = (
            lines
            | "Filter to Continue Processing" >> beam.Filter(lambda line, count: count > 0, beam.pvalue.AsSingleton(row_count))
        )
        _ = (
            row_count
            | "Check If Empty" >> beam.Map(lambda count: print("The input file is empty. Please provide a file with data.") if count == 0 else None)
        )
       
        parsed_rows = (
            non_empty_lines
            | "Parse Lines" >> beam.Map(lambda line, headers_list: parse_lines(line, headers_list[0]), beam.pvalue.AsList(config.headers))
        )
       
        mean_tenure_pcollection = compute_mean_tenure(parsed_rows)
        mean_tenure = (
            mean_tenure_pcollection
          
            | 'ToSingleton' >> beam.CombineGlobally(beam.combiners.ToListCombineFn())  # Combine into a list
            | 'ExtractSingleMean' >> beam.Map(lambda x: x[0])  # Extract the single value from the list
        )
        
        valid_rows = (
            parsed_rows
            | "Filter and Convert to ChurnPred" >> beam.ParDo(filter_churn())
            | "Filter Out None Values" >> beam.Filter(lambda result: result is not None)
        )
     
        processed_data = (
            valid_rows
            
            | "Preprocess Data" >> beam.ParDo(preprocessing_pipeline(),mean_tenure=beam.pvalue.AsSingleton(mean_tenure))
            | "Predict" >> beam.ParDo(predict_churn(rf_model))
        )
        
        formatted_data_pcoll = (
                   processed_data
                   | "Filter None Values" >> beam.Filter(lambda row: row is not None)
                   | "Format Output" >> beam.Map(format_output_row)
        )
        _ = (
              formatted_data_pcoll
              | 'Write to CSV' >> beam.io.WriteToText(
                  args.output, 
                  shard_name_template='', 
                  file_name_suffix='.csv',
                  header='customerID,tenure,PhoneService,Contract,TotalCharges,prediction',
                
              )
        )
       
  
if __name__ == "__main__":
    run()
