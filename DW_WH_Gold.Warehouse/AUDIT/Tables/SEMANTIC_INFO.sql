CREATE TABLE [AUDIT].[SEMANTIC_INFO] (

	[SemModel_Name] varchar(1000) NULL, 
	[SemModel_Description] varchar(4000) NULL, 
	[SemModel_SourceWarehouseDB] varchar(1000) NULL, 
	[Table_ID] int NULL, 
	[Table_Name] varchar(1000) NULL, 
	[Table_Description] varchar(4000) NULL, 
	[Table_Hidden] varchar(100) NULL, 
	[Table_SourceWarehouseTable] varchar(100) NULL, 
	[Field_ID] int NULL, 
	[Field_Type] varchar(100) NULL, 
	[Field_Name] varchar(100) NULL, 
	[Field_Description] varchar(400) NULL, 
	[Field_Hidden] varchar(100) NULL, 
	[Field_Source] varchar(100) NULL, 
	[Field_Folder] varchar(100) NULL
);

