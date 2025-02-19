CREATE TABLE [AUDIT].[MAIN_PIPELINE_RUN_DETAILS] (

	[PL_ID] int NULL, 
	[PL_NAME] varchar(200) NULL, 
	[SOURCE] varchar(200) NULL, 
	[STATUS] varchar(50) NULL, 
	[STARTTIME] datetime2(2) NULL, 
	[ENDTIME] datetime2(2) NULL, 
	[DURATION] time(3) NULL, 
	[RUN_DATE] date NULL, 
	[IS_LATEST_RUN] bit NULL
);

