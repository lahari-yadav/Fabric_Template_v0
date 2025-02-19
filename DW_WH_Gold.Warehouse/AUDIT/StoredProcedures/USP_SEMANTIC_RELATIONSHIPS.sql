CREATE PROCEDURE AUDIT.USP_SEMANTIC_RELATIONSHIPS
AS
BEGIN
    TRUNCATE TABLE AUDIT.SEMANTIC_RELATIONSHIPS

    INSERT INTO AUDIT.SEMANTIC_RELATIONSHIPS
    SELECT
        R.Rel_ID AS REL_ID,
        M.SemModel_Name AS SEMANTIC_MODEL,
        FT.Table_Name AS FROM_TABLE,
        FC.Field_Name AS FROM_COLUMN,
        TT.Table_Name AS TO_TABLE,
        TC.Field_Name AS TO_COLUMN,
        R.Rel_CrossFilterBehavior AS REL_CROSS_FILTER_BEHAVIOR,
        R.Rel_IsActive AS REL_IS_ACTIVE,
        CASE
            WHEN R.Rel_FromCardinality = 2 THEN 'MANY'
            ELSE 'ONE'
        END AS FROM_CARDINALITY,
        CASE
            WHEN R.Rel_ToCardinality = 2 THEN 'MANY'
            ELSE 'ONE'
        END AS TO_CARDINALITY,
        GETDATE() AS LAST_MODIFIED
    FROM DE_LH_CLEAN.dbo.dmv_models_relationships R
    LEFT JOIN DE_LH_CLEAN.dbo.dmv_models M
        ON R.SemModel_ID = M.SemModel_ID
    LEFT JOIN DE_LH_CLEAN.dbo.dmv_models_tables FT
        ON FT.Table_ID = R.Rel_FromTableID AND FT.SemModel_ID = M.SemModel_ID
    LEFT JOIN DE_LH_CLEAN.dbo.dmv_models_columns FC
        ON FC.Field_ID = R.Rel_FromColumnID AND FC.Table_ID = FT.Table_ID AND FC.SemModel_ID = M.SemModel_ID
    LEFT JOIN DE_LH_CLEAN.dbo.dmv_models_tables TT
        ON TT.Table_ID = R.Rel_ToTableID AND TT.SemModel_ID = M.SemModel_ID
    LEFT JOIN DE_LH_CLEAN.dbo.dmv_models_columns TC
        ON TC.Field_ID = R.Rel_ToColumnID AND TC.Table_ID = TT.Table_ID AND TC.SemModel_ID = M.SemModel_ID
END