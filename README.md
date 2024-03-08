**Real Estate Data ETL Project**
This project automates the extraction, transformation, and loading (ETL) of real estate properties data from Zillow Rapid API into Amazon Redshift for analysis and visualization. The workflow is orchestrated using Apache Airflow and leverages AWS Lambda functions for data transformation.

**Project Overview**
Extraction: Real estate properties data is retrieved from Zillow Rapid API.
Loading: The extracted data is loaded into an Amazon S3 bucket.
Transformation: AWS Lambda functions transform the data and load it into another S3 bucket in CSV format.
Orchestration with Apache Airflow: Apache Airflow schedules and monitors the ETL pipeline, ensuring data availability before proceeding.
Loading into Amazon Redshift: Transformed data is loaded into Amazon Redshift for storage and analysis.
Visualization with Amazon QuickSight: Amazon QuickSight connects to the Redshift cluster for data visualization.

**Key Components**
Apache Airflow for workflow orchestration.
AWS Lambda functions for data transformation.
Amazon Redshift for data storage and analytics.
Amazon QuickSight for data visualization.
