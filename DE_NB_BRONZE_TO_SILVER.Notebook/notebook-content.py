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

# CELL ********************

spark.conf.set("spark.sql.parquet.vorder.enabled", "true")
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.microsoft.delta.optimizeWrite.binSize", "1073741824")
spark.conf.set("spark.sql.parquet.int96RebaseModeInRead", "LEGACY")
spark.conf.set("spark.sql.parquet.int96RebaseModeInWrite", "LEGACY")
spark.conf.set("spark.sql.legacy.timeParserPolicy", "CORRECTED")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Parquet to Table + Cleaning

# CELL ********************

# Replace the base abfss path to the incremetal files 
base_path = f"abfss://Fabric_Template@onelake.dfs.fabric.microsoft.com/DE_LH_BronzeSilver.Lakehouse/Files/Bronze_Data/" 
workspace_name = 'Fabric_Template'
lakehouse_name = 'DE_LH_BronzeSilver'

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# CLEANING FUNACTIONS

# CELL ********************

def sanitize(value):
    if value is not None:
        return re.sub(r'[^a-zA-Z0-9]', '_', value)  # Replace non-alphanumeric characters with '_'
    return value

def Clean(df):
    
    # Sanitize column names
    for col_name in df.columns:
            sanitized_col_name = sanitize(col_name)
            df = df.withColumnRenamed(col_name, sanitized_col_name)
   
    string_columns = [field.name for field in df.schema.fields if field.dataType == StringType()]    
    min_date = '1900-01-01'
    
    # Apply trim and replace blank with null for each string column
    for column in string_columns:
        df = df.withColumn(column, when((trim(col(column)) == "") | (col(column) == None), 'UNKNOWN').otherwise(trim(col(column))))
    
    # Get the list of string columns
    date_columns = [field.name for field in df.schema.fields if field.dataType.simpleString() in ['date', 'timestamp']]

    for column in date_columns:
        df = df.withColumn(column,
            when(
                col(column).isNull() | (col(column) < lit(min_date)),  # Check for NULL or less than min_date
                lit(min_date)  # Replace with min_date
            ).otherwise(col(column))  # Keep original value otherwise
        )
    return df



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# MERGING FUNCTION (SCD)

# CELL ********************

from delta.tables import DeltaTable
from pyspark.sql.functions import current_date, lit

def merge_incremental_data( incremental_df,schema_name, table_name, scd_type, primary_key):
    
    full_table_name = schema_name + "." + table_name 
    # Check if table exists
    if spark._jsparkSession.catalog().tableExists(full_table_name):
        
        delta_table = DeltaTable.forPath(spark, f"abfss://{workspace_name}@onelake.dfs.fabric.microsoft.com/{lakehouse_name}.Lakehouse/Tables/{schema_name}/{table_name}")
        
        merge_condition = " AND ".join([f"tgt.{col} = src.{col}" for col in primary_key])
    
        if scd_type == 'SCD 0':  # **SCD Type 0 (Insert-Only, No Updates)**
            incremental_df = incremental_df.withColumn("FABRIC_LOAD_DATE", current_timestamp())
            delta_table.alias("tgt") \
                .merge(incremental_df.alias("src"), merge_condition) \
                .whenNotMatchedInsertAll() \
                .execute()

        elif scd_type == 'SCD 1':  # **SCD Type 1 (Overwrite on Match)**
            incremental_df = incremental_df.withColumn("FABRIC_LOAD_DATE", current_timestamp())
            delta_table.alias("tgt") \
                .merge(incremental_df.alias("src"),merge_condition ) \
                .whenMatchedUpdateAll() \
                .whenNotMatchedInsertAll() \
                .execute()

        elif scd_type == 'SCD 2':  # **SCD Type 2 (Track Historical Changes)**
            incremental_df = incremental_df \
                .withColumn("VALID_FROM", current_timestamp()) \
                .withColumn("VALID_TILL", lit(None)) \
                .withColumn("IS_ACTIVE", lit(1))

            scd2_condition = f"{merge_condition} AND tgt.IS_ACTIVE = 1"

            delta_table.alias("tgt") \
                .merge(incremental_df.alias("src"), scd2_condition) \
                .whenMatchedUpdate(set={
                    "tgt.VALID_TILL": current_timestamp(),
                    "tgt.IS_ACTIVE": lit(0)
                }) \
                .whenNotMatchedInsertAll() \
                .execute()

    else:
        # create table if it doesnot exist  
        print(f"Table {full_table_name} does not exist. Creating it now...")
        if scd_type == 'SCD 2':
            incremental_df = incremental_df \
                .withColumn("VALID_FROM", current_timestamp()) \
                .withColumn("VALID_TILL", lit(None)) \
                .withColumn("IS_ACTIVE", lit(1))
        else:
            incremental_df = incremental_df.withColumn("FABRIC_LOAD_DATE", current_timestamp())

        incremental_df.write.format("delta").mode("overwrite").saveAsTable(full_table_name)
        print(f"Table {full_table_name} created successfully.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Merging Bronze files to silver tables 

# CELL ********************


#from pyspark.sql import functions as F
from pyspark.sql.functions import col,when,trim,current_timestamp,current_date
from pyspark.sql.types import StructType, StructField, StringType, TimestampType,DataType
from datetime import datetime , timedelta
import re

# Define the base abfss path to the incremetal files 
start_date = datetime.now().strftime("%Y-%m-%d") # replace with the start_date string eg: '2024-02-11'
end_date = datetime.now().strftime("%Y-%m-%d")   # replace with end_date string eg: '2024-02-11' ,both dates dates inclusive 

# Fetch master control table
df = spark.read.table('master_control_table')
# CHANGE THE FILTER CONDITIONS to process specific tables only 
df = df.filter( 
    (col('SOURCE') == 'Ecommerce')& 
    (col('PRIMARY_COLUMN_NAME') != 'NULL') & 
    (col('INCREMENTAL_COLUMN_NAME') != 'NULL') )

data_itr = df.rdd.toLocalIterator()

# create schemas of new sources if its not already present 
databases = {db.namespace.split('.')[-1] for db in spark.sql("SHOW DATABASES").collect()}
distinct_sources = [row["DESTINATION_SCHEMA_NAME"] for row in df.select("DESTINATION_SCHEMA_NAME").distinct().collect()]

for source in distinct_sources :
    if source +'`' not in databases :
        print(f" Schema '{source}' does not exist. Creating it now...")
        spark.sql(f"CREATE DATABASE {source}")
        print(f" Schema '{source}' has been created.")

#iterate through master control table 
for row in data_itr:
    try:
        table_name =  row['DESTINATION_TABLE_NAME']  
        schema_name = row['DESTINATION_SCHEMA_NAME']
        current_date =  datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d") 

        while current_date <= end_date:
            month = str(current_date.month).zfill(2)
            day = str(current_date.day).zfill(2)
            file_path = base_path + f'{current_date.year}/{month}/{day}/'
            
            # Read the table from the Lakehouse
            try :
                df = spark.read.parquet(f"{file_path}/{row['SOURCE']}/{row['SOURCE_SCHEMA_NAME']}/{row['DESTINATION_TABLE_NAME']}")
            except Exception as e:
                print(f"Error reading path {file_path}: {e}") 
            # cleaning the incremental data 
            clean_df = Clean(df)
            # fetching primary key column names  
            primary_key = [x for x in row['PRIMARY_COLUMN_NAME'].split(", ")]
            # merginf incremental file to delta table
            merge_incremental_data( clean_df,schema_name,table_name,row['SCD_TYPE'], primary_key)
            current_date += timedelta(days=1)
        
    except Exception as e:
        print(f"Error processing table {table_name}: {e}")   

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

mssparkutils.session.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
