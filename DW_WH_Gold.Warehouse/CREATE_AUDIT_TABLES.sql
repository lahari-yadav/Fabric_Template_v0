-- CREATE AUDIT TABLES
-- MASTER_TABLE_LIST
CREATE TABLE AUDIT.MASTER_TABLE_LIST
(
	[ID] [int]  NULL,
	[SOURCE] [varchar](100)  NULL,
	[SOURCE_TABLE_SCHEMA] [varchar](100)  NULL,
	[SOURCE_TABLE_NAME] [varchar](100)  NULL,
	[DESTINATION] [varchar](100)  NULL,
	[FILE_NAME] [varchar](100)  NULL,
	[FILE_TYPE] [varchar](100)  NULL,
	[DESTINATION_TABLE_SCHEMA] [varchar](100)  NULL,
	[DESTINATION_TABLE_NAME] [varchar](100)  NULL,
	[LOAD_TYPE] [varchar](100)  NULL,
	[INCREMENTAL_COLUMN] [varchar](100)  NULL,
	[STORED_PROCEDURE] [varchar](100)  NULL,
	[SQL_QUERY] [varchar](100)  NULL,
	[PRIMARY_COLUMN_NAME] [varchar](100)  NULL,
	[IN_CLEAN] [int]  NULL,
	[HANDLE_DELETES] [int]  NULL
)
GO


-- MAIN_PIPELINE_RUN_DETAILS
CREATE TABLE AUDIT.MAIN_PIPELINE_RUN_DETAILS
(
	[PL_ID] [int]  NULL,
	[PL_NAME] [varchar](200)  NULL,
	[SOURCE] [varchar](200)  NULL,
	[STATUS] [varchar](50)  NULL,
	[STARTTIME] [datetime2](2)  NULL,
	[ENDTIME] [datetime2](2)  NULL,
	[DURATION] [time](3)  NULL,
	[RUN_DATE] [date]  NULL,
	[IS_LATEST_RUN] [bit]  NULL
)
GO

-- DUPLICATES_SUMMARY
CREATE TABLE AUDIT.DUPLICATES_SUMMARY
(
	TABLE_NAME VARCHAR(100),
	DUPLICATE_COUNT INT,
	DISTINCT_COUNT INT,
	DUPLICATE_DATE DATE
)

-- ROW_COUNT_TABLE
CREATE TABLE AUDIT.ROW_COUNT_TABLE
(
	TABLE_NAME VARCHAR(100),
	PREV_ROW_COUNT INT,
	CURRENT_ROW_COUNT INT
)