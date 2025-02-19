CREATE PROC [AUDIT].[USP_TABLE_COUNT]
    @IS_PREV_ROW_COUNT VARCHAR(10)
AS
BEGIN
    DECLARE @sql NVARCHAR(MAX) = '';
 
    -- Build the dynamic SQL for counting rows in each table
    SELECT @sql += 'SELECT '''+ t.name + ''' AS TableName, COUNT(*) AS Row_Count FROM ' + QUOTENAME(s.name) + '.' + QUOTENAME(t.name) + ' UNION ALL '
    FROM
        sys.tables AS t
    JOIN
        sys.schemas AS s ON t.schema_id = s.schema_id
    WHERE
        t.is_ms_shipped = 0 AND s.name IN ('AGG', 'DETAILED');
        
    -- Remove the trailing 'UNION ALL'
    SET @sql = LEFT(@sql, LEN(@sql) - LEN(' UNION ALL '));
        
    IF @IS_PREV_ROW_COUNT = '1'
    BEGIN
        TRUNCATE TABLE AUDIT.ROW_COUNT_TABLE
        SET @sql = 'INSERT INTO AUDIT.ROW_COUNT_TABLE (TABLE_NAME, PREV_ROW_COUNT) ' + @sql
    END

    IF @IS_PREV_ROW_COUNT = '0'
    BEGIN
        SET @sql = 'UPDATE AUDIT.ROW_COUNT_TABLE SET CURRENT_ROW_COUNT = A.Row_Count FROM (' + @sql
        SET @sql = @sql + ') A WHERE TABLE_NAME = A.TableName'
    END

    PRINT @sql;

    -- Execute the dynamic SQL
    EXEC sp_executesql @sql;
END