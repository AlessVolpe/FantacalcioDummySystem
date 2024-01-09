package database;

import org.jetbrains.annotations.NotNull;

import java.sql.*;

@SuppressWarnings("SqlSourceToSinkFlow") // Bad practice, but it's safe because table creation doesn't require user input at the moment
public class databaseDriver {
    public static void createTable(String connectionString, String tableName, String[] columns, String[] constraints) {
        try(Connection connection = DriverManager.getConnection(connectionString);
            Statement statement = connection.createStatement()) {
            if (doesTableExists(connection, tableName)) {
                throw new SQLException("Table already exists");
            }

            int index = 0;
            StringBuilder sql = new StringBuilder("CREATE TABLE " + tableName.toUpperCase());

            if (columns.length == 0) return;
            while (index < columns.length) {
                sql.append(columns[index].toUpperCase());
                index++;
            }

            index = 0;
            if (constraints.length == 0) statement.executeUpdate(sql.toString());
            else {
               while (index < constraints.length) {
                   sql.append(constraints[index].toUpperCase());
                   index++;
               }
                statement.executeUpdate(sql.toString());
                System.out.println("Created table in given database...");
            }
        } catch (SQLException e) {
            System.err.println(e.getMessage());
        }
    }

    public static boolean isTableEmpty(@NotNull Statement statement, @NotNull String tableName) throws SQLException {
        ResultSet resultSet = statement.executeQuery("SELECT * FROM " + tableName.toUpperCase());
        return !resultSet.next();
    }

    public static boolean doesTableExists(@NotNull Connection connection, String tableName) throws SQLException {
        return connection
                    .getMetaData()
                    .getTables(null, null, tableName.toUpperCase(),new String[] {"TABLE"})
                    .next();
    }
}
