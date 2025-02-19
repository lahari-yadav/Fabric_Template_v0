CREATE PROCEDURE AUDIT.USP_SEMANTIC_INFO
AS
BEGIN
	DROP TABLE AUDIT.SEMANTIC_INFO; 

    SELECT * INTO AUDIT.SEMANTIC_INFO 
    FROM (
        SELECT
            C.SemModel_Name,
            C.SemModel_Description,
            D.Expression_Desc as SemModel_SourceWarehouseDB,
            B.Table_ID,
            B.Table_Name,
            B.Table_Description,
            B.Table_Hidden,
            B.Table_Source as Table_SourceWarehouseTable,
            A.Field_ID,
            A.Field_Type,
            A.Field_Name,
            A.Field_Description,
            A.Field_Hidden,
            A.Field_Source,
            '' as Field_Folder
        FROM DE_LH_CLEAN.dbo.dmv_models_columns A
        LEFT JOIN DE_LH_CLEAN.dbo.dmv_models_tables B
            ON A.SemModel_ID = B.SemModel_ID AND A.Table_ID = B.Table_ID
        LEFT JOIN DE_LH_CLEAN.dbo.dmv_models C
            ON A.SemModel_ID = C.SemModel_ID
        LEFT JOIN DE_LH_CLEAN.dbo.dmv_models_source D
            ON A.SemModel_ID = D.SemModel_ID
        WHERE D.Expression_Type = 'DatabaseQuery'
        UNION
        SELECT
            C.SemModel_Name,
            C.SemModel_Description,
            D.Expression_Desc as SemModel_SourceWarehouseDB,
            B.Table_ID,
            B.Table_Name,
            B.Table_Description,
            B.Table_Hidden,
            B.Table_Source as Table_SourceWarehouseTable,
            A.Field_ID,
            A.Field_Type,
            A.Field_Name,
            A.Field_Description,
            A.Field_Hidden,
            A.Field_Source,
            A.Field_Folder as Field_Folder
        FROM DE_LH_CLEAN.dbo.dmv_models_measures A
        LEFT JOIN DE_LH_CLEAN.dbo.dmv_models_tables B
            ON A.SemModel_ID = B.SemModel_ID AND A.Table_ID = B.Table_ID
        LEFT JOIN DE_LH_CLEAN.dbo.dmv_models C
            ON A.SemModel_ID = C.SemModel_ID
        LEFT JOIN DE_LH_CLEAN.dbo.dmv_models_source D
            ON A.SemModel_ID = D.SemModel_ID
        WHERE D.Expression_Type = 'DatabaseQuery'
    ) A
    ORDER BY SemModel_Name, Table_Name, Field_Name
END