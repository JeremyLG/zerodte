import duckdb

duckdb.sql(
    """
    install sqlite;
    load sqlite;
    attach 'data/tat/data.db3' as tat (type sqlite);
    use tat;
    export database 'data/tat/database' (FORMAT CSV, HEADER 1, DELIMITER ';');
    """
)
