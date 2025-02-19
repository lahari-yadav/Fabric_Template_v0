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
# META       "default_lakehouse_workspace_id": "cf6b9fab-9075-4a96-9da7-cdd8f4007577"
# META     }
# META   }
# META }

# CELL ********************

from pyspark.sql.functions import expr, col
import re 
def sanitize(value):
    if value is not None:
        return re.sub(r'[^a-zA-Z0-9]', '_', value)  # Replace non-alphanumeric characters with '_'
    return value

# Load master_control_table
master_df = spark.read.table('master_control_table')
master_df = master_df.filter( 
    (col('SOURCE') == 'Ecommerce')& 
    (col('PRIMARY_COLUMN_NAME') != 'NULL') & 
    (col('INCREMENTAL_COLUMN_NAME') != 'NULL'))


# Prepare an empty list to store updated values
updated_records = []

# Loop through each table in master_control_table
for row in master_df.collect():
    id = row["ID"]
    table_schema = row["DESTINATION_SCHEMA_NAME"]
    table_name = row["DESTINATION_TABLE_NAME"]
    incremental_column = sanitize(row["INCREMENTAL_COLUMN_NAME"])

    # Fetch max incremental value
    sql_query = f"SELECT MAX({incremental_column}) FROM {table_schema}.{table_name}"
    
    try:
        last_load_max = spark.sql(sql_query).collect()[0][0]  # Fetch max value efficiently
        
        if last_load_max is not None:
            # Construct SQL_QUERY dynamically
            sql_query_text = (
                f"SELECT * FROM {row.SOURCE_SCHEMA_NAME}.{table_name} "
                f"WHERE [{row.INCREMENTAL_COLUMN_NAME}] > cast('{last_load_max}' as datetime)" 
            )

            # Append updated row
            updated_records.append((id,table_schema, table_name, last_load_max, sql_query_text))

    except Exception as e:
        print(f"Error processing {table_schema}.{table_name}: {str(e)}")

# Convert updated records to a DataFrame
columns = ["id","destination_schema_name", "destination_table_name", "last_load_max", "SQL_QUERY"]
updates_df = spark.createDataFrame(updated_records, columns)

# Use Delta Lake MERGE INTO to update only changed rows
updates_df.createOrReplaceTempView("updates")

merge_query = f"""
MERGE INTO master_control_table AS target
USING updates AS source
ON target.id = source.id
WHEN MATCHED THEN 
  UPDATE SET 
    target.last_load_max = source.last_load_max,
    target.SQL_QUERY = source.SQL_QUERY
"""

# Execute the MERGE query
spark.sql(merge_query)

print("Master control table updated successfully using MERGE.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
