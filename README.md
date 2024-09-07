
# Churn Prediction Pipeline

This project is designed to process customer data and predict churn using a pre-trained machine learning model. The pipeline is built using Apache Beam, and the entire workflow is managed through Docker and Docker Compose. Additionally, the project integrates WhyLogs for data profiling and monitoring, and Prometheus and Grafana for system monitoring.



## Table of Contents

- [Project Structure](#project-structure)
  - [file_watcher.py](#1-file_watcherpy)
  - [prediction_batch_pipeline.py](#2-prediction_batch_pipelinepy)
  - [config.py](#4-configpy)
  - [Docker Setup](#5-docker-setup)
    - [Dockerfile](#dockerfile)
    - [docker-compose.yaml](#docker-composeyaml)
  - [Makefile](#6-makefile)
  - [Optional: .env File](#7-optional-env-file)
- [How Everything Works Together](#how-everything-works-together)
  - [Workflow](#workflow)
  - [Configuration](#configuration)
- [Setup and Usage](#setup-and-usage)
  - [Prerequisites](#prerequisites)
  - [Steps](#steps)
    - [Clone the Repository](#clone-the-repository)
    - [Build the Docker Image](#build-the-docker-image)
    - [Start the Services](#start-the-services)
    - [Place Input Files](#place-input-files)
    - [Monitor the Pipeline](#monitor-the-pipeline)
    - [WhyLogs Profiling](#whylogs-profiling)
    - [Cleanup](#cleanup)
- [Conclusion](#conclusion)





## Project Structure

### 1. `file_watcher.py`

- **Purpose**: This script monitors a specified directory for new CSV files. When a new file is detected, it triggers the data processing pipeline (`prediction_batch_pipeline.py`), and if configured, also triggers WhyLogs profiling.
- **Key Features**:
  - Monitors the input directory for new files.
  - Triggers the data processing pipeline.
  - Optionally triggers WhyLogs profiling based on the configuration.
  - Starts a Prometheus metrics server for monitoring.


### 2. `prediction_batch_pipeline.py`

- **Purpose**: This script is the core of the data processing pipeline. It reads input data, preprocesses it, applies the churn prediction model, and outputs the results to a specified location.
- **Key Features**:
  - Validates and preprocesses input data.
  - Applies a pre-trained RandomForest model for churn prediction.
  - Outputs results in a CSV format.


### 34. `config.py`

- **Purpose**: Centralized configuration for the entire project, including paths, logging settings, and WhyLogs configurations.

- **Key Features**:
  - Specifies paths for models, logs, and output files.
  - Configures logging settings.
  - Includes WhyLogs-related configurations such as organization ID, API key, and dataset ID.
  - Allows enabling or disabling WhyLogs profiling.


### 4. Docker Setup

#### Dockerfile

- **Purpose**: Defines the environment for running the churn prediction pipeline. 
    It installs necessary dependencies, sets up directories, and configures the environment.

- **Key Features**:
  - Uses the official Python 3.9 image.
  - Installs necessary dependencies including Apache Beam, Scikit-Learn, WhyLogs, and Pandas.
  - Sets up volumes for input, output, and logs.
  - Configures the environment and sets the working directory.
  - Includes a command to run `file_watcher.py` as the entry point.



#### docker-compose.yaml

- **Purpose**: Orchestrates the different services required for the churn prediction pipeline, 
    including the batch processing service,   WhyLogs integration, Prometheus, and Grafana.

- **Key Services**:

  - **batch-process-predict**: Runs the `file_watcher.py` script to monitor input files and process them through the pipeline.
  - **whylogs**: Runs the `whylogs_integration.py` script to profile data and upload results to WhyLabs.
  - **prometheus**: Collects metrics from the pipeline and WhyLogs and makes them available for monitoring.
  - **grafana**: Visualizes the metrics collected by Prometheus.


### 5. Makefile

- **Purpose**: Provides convenient commands to build, test, and manage the project.

- **Key Features**:
  - Commands for building Docker images.
  - Commands for running tests and formatting code.
  - Commands for managing the environment and dependencies.




## How Everything Works Together

### Workflow

1. **File Detection**:
   - `file_watcher.py` monitors the `/code/input-files` directory for new CSV files.
   - When a new file is detected, it triggers the `prediction_batch_pipeline.py` to process the data.

2. **Data Processing**:
   - `prediction_batch_pipeline.py` validates and preprocesses the input data, applies the churn prediction model, and outputs the results to `/code/output-files`.

3. **Monitoring**:
   - Prometheus collects metrics from the pipeline and WhyLogs and provides them for monitoring.
   - Grafana visualizes these metrics, allowing you to monitor the health and performance of the pipeline.



### Configuration

- The entire pipeline is configured through `config.py`, which centralizes all the settings, including paths, logging levels, and WhyLogs credentials.
- Docker and Docker Compose manage the environment, ensuring that all dependencies are correctly installed and that all services are properly orchestrated.



## Setup and Usage

### Prerequisites

- Docker and Docker Compose installed on your machine.



### Steps

#### Clone the Repository

```bash
git clone https://github.com/miriezrubelsky/churn-project-latest.git
cd churn-project-latest


#### Build the Docker Image 
```bash
docker-compose build


#### Start the Services
```bash
docker-compose up


#### Place Input Files
Place your input CSV files in the /code/input-files directory. 
the file_watcher.py script will automatically detect them and process them through the pipeline.


#### Monitor the Pipeline
Access Grafana at http://localhost:3000 to visualize metrics collected by Prometheus.





├─ datasource.yml
├─ docker-compose.yaml
├─ Dockerfile
├─ file_watcher.py
├─ grafana-dashboard.json
├─ makefile
├─ prediction_batch_pipeline.py
├─ prometheus.yml
├─ README.md
├─ setup.py
└─ src
   ├─ churn_prediction_pipeline
   │  ├─ config
   │  │  ├─ config.py
   │  │  └─ __init__.py
   │  ├─ data
   │  │  ├─ churn_pred_data.py
   │  │  ├─ internal_churn_pred_data.py
   │  │  ├─ output_churn_pred_data.py
   │  │  └─ __init__.py
   │  ├─ logs
   │  │  └─ .empty
      ├─ filter_churn.py 
   │  ├─ predict_churn.py
   │  ├─ preprocessing_pipeline.py
   │  ├─ processing
   │  │  ├─ data_handling.py
   │  │  ├─ preprocessing.py
   │  │  └─ __init__.py
   │  ├─ README.md
   │  ├─ trained_model
   │  │  ├─ churn_model.pickle
   │  │  └─ __init__.py
   │  ├─ VERSION
   │  └─ __init__.py
   ├─ README.md
   ├─ requirements.txt
   └─ tests
      ├─ test_filter_churn.py
      ├─ test_predict_churn.py
      ├─ test_preprocessing_pipeline.py
      └─ __init__.py

