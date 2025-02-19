# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

# MAGIC %%configure -f
# MAGIC {  
# MAGIC     "defaultLakehouse": {  
# MAGIC         "name": "DE_LH_CLEAN"  
# MAGIC     }
# MAGIC }

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - We primarily use this to get the DICTIONARY_LAST_ACCESSED, which gives us information on the most used / queried columns in each semantic model.
# - Using this we can pre-warm the most frequently used columns in semantic models to improve performance for user.

# CELL ********************

import sempy.fabric as fabric
import datetime
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, BooleanType, TimestampType
from pyspark.sql.functions import lit

# provide WORKSPACE name
Workspace_fabic = ""
Datasets_fabric = fabric.list_datasets(workspace=Workspace_fabic)

schema = StructType([
    StructField("MEASURE_GROUP_NAME", StringType(), True),
    StructField("ATTRIBUTE_NAME", StringType(), True),
    StructField("DATATYPE", StringType(), True),
    StructField("DICTIONARY_SIZE", IntegerType(), True),
    StructField("DICTIONARY_ISPAGEABLE", BooleanType(), True),
    StructField("DICTIONARY_ISRESIDENT", BooleanType(), True),
    StructField("DICTIONARY_TEMPERATURE", FloatType(), True),
    StructField("DICTIONARY_LAST_ACCESSED", TimestampType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("SEMANTIC_MODEL", StringType(), True)
])


for row in Datasets_fabric.itertuples():
    print(row._1)
    # semantic model names start with DM - so only bring semantic model
    if row._1[:2] == "DM":
        try:
            df = fabric.evaluate_dax(
                dataset=row._1, 
                dax_string = """SELECT 
                    MEASURE_GROUP_NAME,
                    ATTRIBUTE_NAME ,
                    DATATYPE ,
                    DICTIONARY_SIZE ,
                    DICTIONARY_ISPAGEABLE ,
                    DICTIONARY_ISRESIDENT ,
                    DICTIONARY_TEMPERATURE ,
                    DICTIONARY_LAST_ACCESSED
                
                        FROM $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS 
                        ORDER BY [DICTIONARY_TEMPERATURE] DESC
                """,
                workspace = Workspace_fabic)
            # Append timestamp column
            now = datetime.datetime.now()
            df["timestamp"] = now
            df["SEMANTIC_MODEL"] = row._1

            try:
                spark_df = spark.createDataFrame(df, schema)

                spark_df.write.format("delta").mode("append")\
                    .option("delta.columnMapping.mode", "name")\
                    .option("mergeSchema", "true")\
                    .saveAsTable("DE_LH_CLEAN.dmv_log")
            except Exception as e:
                print(f'Failed to save df for: {row._1}, error: {e}')

        except Exception as e:
            print(f'Error processing semantic model: {row._1}, error: {e}')
    else:
        print("-")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
