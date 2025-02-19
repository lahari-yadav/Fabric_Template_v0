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

# CELL ********************

import pyspark.sql.functions as F
df_datasets = fabric.list_datasets()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Run DAX - To load columns in memory

# CELL ********************

# provide the names of semantic models for which you wnat to pre-warm the columns
semantic_models = []

for name in semantic_models:
    df = spark.read.table('dmv_log')
    df = df.where(df.SEMANTIC_MODEL == name)
    # Get columns with top 20 temperature
    df = df.select('MEASURE_GROUP_NAME', 'ATTRIBUTE_NAME', 'DICTIONARY_TEMPERATURE').groupBy('MEASURE_GROUP_NAME', 'ATTRIBUTE_NAME').agg({'DICTIONARY_TEMPERATURE': 'sum'})
    df = df.withColumnRenamed('sum(DICTIONARY_TEMPERATURE)', 'SUM')
    df = df.orderBy(df.SUM.desc())
    df = df.limit(20)
    # it will only warm the top 20 columns
    
    # Create DAX
    count = 1
    myDax = "EVALUATE ROW(\n"
    for row in df.collect():
        lower = any(char.islower() for char in row.MEASURE_GROUP_NAME)
        if not lower:
            myDax = myDax + '"COUNT_' + str(count) + '", COUNT(' + row.MEASURE_GROUP_NAME + '[' + row.ATTRIBUTE_NAME + ']),\n'
            count += 1
    myDax = myDax[:-2]
    myDax = myDax + ')'

    # Execute DAX
    fabric.evaluate_dax( name, myDax).head(20)
    # print(myDax)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
