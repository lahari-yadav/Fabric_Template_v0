CREATE PROCEDURE [AUDIT].[USP_DUPLICATES_SUMMARY]
AS
BEGIN    
    -- Declare Variables
	DECLARE @TABLE_NAME NVARCHAR(4000);
	DECLARE @TABLE_SCHEMA NVARCHAR(4000) = 'AUDIT';
	DECLARE @RowCount INT;
	DECLARE @CurrentRow INT = 1;
	DECLARE @RowCountColumn INT;
	DECLARE @CurrentRowColumn INT = 1;
	DECLARE @SQL NVARCHAR(4000);

	-- Temporary table to simulate cursor behavior
	-- Check if the temporary table already exists and drop it if it does
	IF OBJECT_ID('tempdb..#CursorTable') IS NOT NULL
		DROP TABLE #CursorTable;
	CREATE TABLE #CursorTable (RowNum INT IDENTITY(1,1), Table_Name NVARCHAR(4000));
	INSERT INTO #CursorTable (Table_Name) SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'AUDIT' AND TABLE_NAME LIKE '%_DUPLICATES%';

	SELECT @RowCount = COUNT(*) FROM #CursorTable;

	-- Truncate & Load
	IF EXISTS (SELECT 1 FROM [AUDIT].[DUPLICATES_SUMMARY])
	BEGIN
		TRUNCATE TABLE [AUDIT].[DUPLICATES_SUMMARY]
	END

	-- Loop through each row in the cursor table
	WHILE @CurrentRow <= @RowCount
	BEGIN
		SELECT @TABLE_NAME = Table_Name FROM #CursorTable WHERE RowNum = @CurrentRow;

		SET @SQL = N'INSERT INTO [AUDIT].[DUPLICATES_SUMMARY] (TABLE_NAME, DUPLICATE_COUNT)
				SELECT ''' + @TABLE_NAME + ''' AS TABLE_NAME, COUNT(*) 
				FROM [' + @TABLE_SCHEMA + '].[' + @TABLE_NAME + ']
				WHERE CAST(DUPLICATE_DATE AS DATE) = GETDATE();';
				-- comment WHERE to see all duplicates
		EXEC sp_executesql @SQL;

		SET @CurrentRow = @CurrentRow + 1;

		-- Check for tables that have duplicates
		IF OBJECT_ID('tempdb..#CursorTableColumns') IS NOT NULL
			DROP TABLE #CursorTableColumns;
		CREATE TABLE #CursorTableColumns (RowNum INT IDENTITY(1,1), Column_Name NVARCHAR(4000));

		IF (SELECT DUPLICATE_COUNT FROM [AUDIT].[DUPLICATES_SUMMARY] WHERE TABLE_NAME = @TABLE_NAME) > 0
		BEGIN
			-- Insert Column Name to #CursorTableColumns
			INSERT INTO #CursorTableColumns (Column_Name) (
				SELECT COLUMN_NAME
				FROM INFORMATION_SCHEMA.COLUMNS
				WHERE TABLE_NAME = @TABLE_NAME AND COLUMN_NAME <> 'DUPLICATE_DATE'
			)

			SET @SQL = ''
			SELECT @RowCountColumn = COUNT(*) FROM #CursorTableColumns
			SET @CurrentRowColumn = 1;
			WHILE @CurrentRowColumn <= @RowCountColumn
			BEGIN
				SET @SQL = @SQL + (SELECT Column_Name FROM #CursorTableColumns WHERE RowNum = @CurrentRowColumn)
				IF @CurrentRowColumn != @RowCountColumn
				BEGIN
					SET @SQL = @SQL + ', '
				END
				SET @CurrentRowColumn = @CurrentRowColumn + 1
			END

			SET @SQL = 'SELECT COUNT(*) FROM (SELECT DISTINCT ' + @SQL + ' FROM ' + @TABLE_SCHEMA + '.' + @TABLE_NAME + ') A';
		SET @SQL = N'UPDATE AUDIT.DUPLICATES_SUMMARY
				SET DISTINCT_COUNT = (' + @SQL + ')
				WHERE TABLE_NAME = ''' + @TABLE_NAME + '''
				AND CAST(DUPLICATE_DATE AS DATE) = GETDATE();'
				-- comment WHERE to see all duplicates
		PRINT @SQL
		EXEC sp_executesql @SQL;
		END
	END
	DROP TABLE #CursorTable;
END;