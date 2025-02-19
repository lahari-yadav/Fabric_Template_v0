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

# **Drop tables (full load)**

# CELL ********************

# MAGIC %%sql
# MAGIC DROP TABLE dmv_models_source;
# MAGIC DROP TABLE dmv_models;
# MAGIC DROP TABLE dmv_models_tables;
# MAGIC DROP TABLE dmv_models_columns;
# MAGIC DROP TABLE dmv_models_measures;
# MAGIC DROP TABLE dmv_models_relationships;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Write tables**

# MARKDOWN ********************

# The following code will create dmv_models_.. tables in clean layer, which can be joined to create tables that give us info about semantic tables, and relationships between the tables in semantic model

# CELL ********************

import sempy.fabric as fabric
import datetime
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, BooleanType, TimestampType
from pyspark.sql.functions import lit

# provide workspace name
Workspace_fabic = ""
Datasets_fabric = fabric.list_datasets(workspace=Workspace_fabic)

schema_models_sourcedb = StructType([
    StructField("Expression_Type", StringType(), True),
    StructField("Expression_Desc", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("SemModel_ID", StringType(), True)
])
schema_models = StructType([
    StructField("SemModel_Name", StringType(), True),
    StructField("SemModel_Description", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("SemModel_ID", StringType(), True)
])
schema_models_tables = StructType([
    StructField("Table_ID", IntegerType(), True),
    StructField("Table_Name", StringType(), True),
    StructField("Table_Description", StringType(), True),
    StructField("Table_Hidden", BooleanType(), True),
    StructField("Table_Source", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("SemModel_ID", StringType(), True)
])
schema_models_columns = StructType([
    StructField("Field_ID", IntegerType(), True),
    StructField("Table_ID", IntegerType(), True),
    StructField("Field_Name", StringType(), True),
    StructField("Field_Description", StringType(), True),
    StructField("Field_Type", StringType(), True),
    StructField("Field_Hidden", BooleanType(), True),
    StructField("Field_Source", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("SemModel_ID", StringType(), True)
])
schema_models_measures = StructType([
    StructField("Field_ID", IntegerType(), True),
    StructField("Table_ID", IntegerType(), True),
    StructField("Field_Name", StringType(), True),
    StructField("Field_Description", StringType(), True),
    StructField("Field_Type", StringType(), True),
    StructField("Field_Hidden", BooleanType(), True),
    StructField("Field_Source", StringType(), True),
    StructField("Field_Folder", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("SemModel_ID", StringType(), True)
])
schema_models_relationships = StructType([
    StructField("Rel_ID", StringType(), True),
    StructField("Rel_CrossFilterBehavior", IntegerType(), True),
    StructField("Rel_IsActive", BooleanType(), True),
    StructField("Rel_FromTableID", IntegerType(), True),
    StructField("Rel_FromColumnID", IntegerType(), True),
    StructField("Rel_FromCardinality", IntegerType(), True),
    StructField("Rel_ToTableID", IntegerType(), True),
    StructField("Rel_ToColumnID", IntegerType(), True),
    StructField("Rel_ToCardinality", IntegerType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("SemModel_ID", StringType(), True)
])


for row in Datasets_fabric.itertuples():
    print(f'{row._1} : Processing',end="\r")
    if row._1[:2] == "DM":
        try:
            #source database query
            df_sourcedb = fabric.evaluate_dax(
                dataset=row._1, 
                dax_string = """SELECT [NAME] as Expression_Type,[EXPRESSION] as Expression_Desc FROM $System.TMSCHEMA_EXPRESSIONS""",
                workspace = Workspace_fabic)
            #Model name and description
            df_models = fabric.evaluate_dax(
                dataset=row._1, 
                dax_string = """SELECT [CATALOG_NAME] as SemModel_Name, [DESCRIPTION] as SemModel_Description from $SYSTEM.MDSCHEMA_CUBES""",
                workspace = Workspace_fabic)
            #Table names and descriptions
            df_models_tables = fabric.evaluate_dax(
                dataset=row._1, 
                dax_string = """SELECT [ID] as Table_ID,[NAME] as Table_Name,[DESCRIPTION] as Table_Description,[ISHIDDEN] as Table_Hidden,[SOURCELINEAGETAG] as Table_Source from $SYSTEM.TMSCHEMA_TABLES""",
                workspace = Workspace_fabic)
            #Column names and descriptions
            df_models_columns = fabric.evaluate_dax(
                dataset=row._1, 
                dax_string = """SELECT [ID] as Field_ID,[TABLEID] as Table_ID,[EXPLICITNAME] as Field_Name,[DESCRIPTION] as Field_Description, 'Data Column' as Field_Type, [ISHIDDEN] as Field_Hidden,[SOURCECOLUMN] as Field_Source from $SYSTEM.TMSCHEMA_COLUMNS""",
                workspace = Workspace_fabic)
            #Measure names and descriptions
            df_models_measures = fabric.evaluate_dax(
                dataset=row._1, 
                dax_string = """SELECT [ID] as Field_ID,[TABLEID] as Table_ID,[NAME] as Field_Name,[DESCRIPTION] as Field_Description, 'Measure' as Field_Type, [ISHIDDEN] as Field_Hidden,[EXPRESSION] as Field_Source,[DISPLAYFOLDER] as Field_Folder from $SYSTEM.TMSCHEMA_MEASURES""",
                workspace = Workspace_fabic)
            #Relationships
            df_models_relationships = fabric.evaluate_dax(
                dataset=row._1, 
                dax_string = """select [NAME] as Rel_ID,[CrossFilteringBehavior] as Rel_CrossFilterBehavior,[ISACTIVE] as Rel_IsActive,[FROMTABLEID] as Rel_FromTableID,[FROMCOLUMNID] as Rel_FromColumnID,[FROMCARDINALITY] as Rel_FromCardinality,[TOTABLEID] as Rel_ToTableID,[TOCOLUMNID] as Rel_ToColumnID,[TOCARDINALITY] as Rel_ToCardinality from $SYSTEM.TMSCHEMA_RELATIONSHIPS""",
                workspace = Workspace_fabic)
            
            # Append timestamp column
            now = datetime.datetime.now()
            df_sourcedb["timestamp"] = now
            df_models["timestamp"] = now
            df_models_tables["timestamp"] = now
            df_models_columns["timestamp"] = now
            df_models_measures["timestamp"] = now
            df_models_relationships["timestamp"] = now
            
            # Append sem model ID
            df_sourcedb["SemModel_ID"] = row._2
            df_models["SemModel_ID"] = row._2
            df_models_tables["SemModel_ID"] = row._2
            df_models_columns["SemModel_ID"] = row._2
            df_models_measures["SemModel_ID"] = row._2
            df_models_relationships["SemModel_ID"] = row._2

            try:
                #create spark DFs
                spark_df_sourcedb = spark.createDataFrame(df_sourcedb, schema_models_sourcedb)
                spark_df_models = spark.createDataFrame(df_models, schema_models)
                spark_df_models_tables = spark.createDataFrame(df_models_tables, schema_models_tables)
                spark_df_models_columns = spark.createDataFrame(df_models_columns, schema_models_columns)
                spark_df_models_measures = spark.createDataFrame(df_models_measures, schema_models_measures)
                spark_df_models_relationships = spark.createDataFrame(df_models_relationships, schema_models_relationships)
                
                #write spark DFs to Delta
                spark_df_sourcedb.write.format("delta").mode("append")\
                    .option("delta.columnMapping.mode", "name")\
                    .option("mergeSchema", "true")\
                    .saveAsTable("dmv_models_source")
                spark_df_models.write.format("delta").mode("append")\
                    .option("delta.columnMapping.mode", "name")\
                    .option("mergeSchema", "true")\
                    .saveAsTable("dmv_models")
                spark_df_models_tables.write.format("delta").mode("append")\
                    .option("delta.columnMapping.mode", "name")\
                    .option("mergeSchema", "true")\
                    .saveAsTable("dmv_models_tables")
                spark_df_models_columns.write.format("delta").mode("append")\
                    .option("delta.columnMapping.mode", "name")\
                    .option("mergeSchema", "true")\
                    .saveAsTable("dmv_models_columns")
                spark_df_models_measures.write.format("delta").mode("append")\
                    .option("delta.columnMapping.mode", "name")\
                    .option("mergeSchema", "true")\
                    .saveAsTable("dmv_models_measures")
                spark_df_models_relationships.write.format("delta").mode("append")\
                    .option("delta.columnMapping.mode", "name")\
                    .option("mergeSchema", "true")\
                    .saveAsTable("dmv_models_relationships")
                
                print("\033[F", end="")
                print(f'{row._1}: Saved Metadata')
            except Exception as e:
                print("\033[F", end="")
                print(f'{row._1}: Failed to save metadata, error: {e}')

        except Exception as e:
            print("\033[F", end="")
            print(f'{row._1}: Error processing semantic model, error: {e}')
    else:
        print("\033[F", end="")
        print(f'{row._1}: Skipped saving metadata')

print('Completed')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# **Query output**

# CELL ********************

# MAGIC %%sql
# MAGIC --select count(*),count(distinct SemModel_ID) from dmv_models;
# MAGIC --select count(*),count(distinct SemModel_ID) from dmv_models_source;
# MAGIC --select count(*),count(distinct concat(SemModel_ID,Table_ID)) from dmv_models_tables;
# MAGIC --select count(*),count(distinct concat(SemModel_ID,Table_ID,Field_ID)) from dmv_models_columns;
# MAGIC --select count(*),count(distinct concat(SemModel_ID,Table_ID,Field_ID)) from dmv_models_measures;
# MAGIC --select count(*),count(distinct Rel_ID) from dmv_models_relationships;
# MAGIC 
# MAGIC --select * into SEMANTIC_INFO from (
# MAGIC select * from (
# MAGIC select 
# MAGIC     C.SemModel_Name,C.SemModel_Description,D.Expression_Desc as SemModel_SourceWarehouseDB,
# MAGIC     B.Table_ID,B.Table_Name,B.Table_Description,B.Table_Hidden,B.Table_Source as Table_SourceWarehouseTable,
# MAGIC     A.Field_ID,A.Field_Type,A.Field_Name,A.Field_Description,A.Field_Hidden,A.Field_Source,'' as Field_Folder
# MAGIC from dmv_models_columns A
# MAGIC left join dmv_models_tables B
# MAGIC on A.SemModel_ID=B.SemModel_ID AND A.Table_ID=B.Table_ID
# MAGIC left join dmv_models C
# MAGIC on A.SemModel_ID=C.SemModel_ID
# MAGIC left join dmv_models_source D
# MAGIC on A.SemModel_ID=D.SemModel_ID
# MAGIC where D.Expression_Type = 'DatabaseQuery'
# MAGIC UNION
# MAGIC select 
# MAGIC     C.SemModel_Name,C.SemModel_Description,D.Expression_Desc as SemModel_SourceWarehouseDB,
# MAGIC     B.Table_ID,B.Table_Name,B.Table_Description,B.Table_Hidden,B.Table_Source as Table_SourceWarehouseTable,
# MAGIC     A.Field_ID,A.Field_Type,A.Field_Name,A.Field_Description,A.Field_Hidden,A.Field_Source,A.Field_Folder as Field_Folder
# MAGIC from dmv_models_measures A
# MAGIC left join dmv_models_tables B
# MAGIC on A.SemModel_ID=B.SemModel_ID AND A.Table_ID=B.Table_ID
# MAGIC left join dmv_models C
# MAGIC on A.SemModel_ID=C.SemModel_ID
# MAGIC left join dmv_models_source D
# MAGIC on A.SemModel_ID=D.SemModel_ID
# MAGIC where D.Expression_Type = 'DatabaseQuery'
# MAGIC )
# MAGIC where SemModel_Name='DM_LEGACY_SALES'
# MAGIC order by SemModel_Name,Table_Name,Field_Name
# MAGIC --limit 10
# MAGIC ;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
