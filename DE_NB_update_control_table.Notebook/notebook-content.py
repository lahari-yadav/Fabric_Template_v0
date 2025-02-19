# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "b726adfa-518b-4fad-9ae3-2250b9b95ecf",
# META       "default_lakehouse_name": "DE_LH_BronzeSilver",
# META       "default_lakehouse_workspace_id": "cf6b9fab-9075-4a96-9da7-cdd8f4007577",
# META       "known_lakehouses": [
# META         {
# META           "id": "b726adfa-518b-4fad-9ae3-2250b9b95ecf"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# Create master control table in an excel sheet with the following schema. 
# # Master Control Table
# 
# | ID  | SOURCE | SOURCE_SCHEMA_NAME | SOURCE_TABLE_NAME | DESTINATION_FILE_PATH | DESTINATION_FILE_NAME | DESTINATION_FILE_TYPE | DESTINATION_SCHEMA_NAME | DESTINATION_TABLE_NAME | LOAD_TYPE | SCD_TYPE | INCREMENTAL_COLUMN | PRIMARY_COLUMN_NAME | HANDLE_DELETES | MAX_INCREMENTAL_VALUE | SQL_QUERY |
# |----|--------|-------------------|------------------|--------------------|-----------------|----------------|-------------------|------------------|----------|---------|-----------------|-----------------|---------------|-------------------|-----------|
# | 1  | olist  | dbo               | customers        | DE_LH_RAW/Files/Brazilian_dataset_parquet | customers | parquet | olist | customers | Incremental | 1 | last_modified_date | customer_id | 0 | 1900-01-01 |
# 
# upload the csv file of the master control table in the lakehouse
# 
# 	
# 
# Fetch afbs file path of master control table csv file 


# CELL ********************

# REPLACE the file path with the master_control_table file path 
file_path = 'abfss://Fabric_Template@onelake.dfs.fabric.microsoft.com/DE_LH_BronzeSilver.Lakehouse/Files/Master_Table_List_Template.csv'


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Generating SQL_QUERY column and sanitizing table and primary column names

# CELL ********************

from pyspark.sql.utils import AnalysisException
from pyspark.sql.functions import col,udf,expr
from pyspark.sql.types import StringType
import re

# function to replace special characters
def sanitize(value):
    if value is not None:
        return re.sub(r'[^a-zA-Z0-9]', '_', value)  # Replace non-alphanumeric characters with '_'
    return value
def column_split(column_names):
    if column_names :
        ','.join([sanitize(x) for x in column_names.split(',')])
    return column_names
    

df = (spark.read
        .format('csv')
        .option('header' , True)
        .option('inforSchema' , True)
        .load(file_path))


# Register UDF
sanitized_table_udf = udf(sanitize,StringType())
sanitized_column_udf = udf(column_split,StringType())

# Add new column with transformed values
df = df.withColumn("DESTINATION_TABLE_NAME", sanitized_table_udf(df["SOURCE_TABLE_NAME"]))
df = df.withColumn("DESTINATION_FILE_NAME",df["DESTINATION_TABLE_NAME"] )
df = df.withColumn("PRIMARY_COLUMN_NAME", sanitized_column_udf(df["PRIMARY_COLUMN_NAME"]))
df = df.withColumn(
    "SQL_QUERY",
    expr("concat('SELECT *  FROM ', SOURCE_SCHEMA_NAME, '.', SOURCE_TABLE_NAME)")
)


df.write.option('overwriteSchema',True).mode("overwrite").saveAsTable("master_control_table")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
