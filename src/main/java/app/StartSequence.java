package app;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ResourceBundle;

public class StartSequence {
    public static ResourceBundle propertyLoader() {
        return ResourceBundle.getBundle("app.properties");
    }

    public static void testDBConnection(String connectionString) {
        try {
            Connection connection = DriverManager.getConnection(connectionString);
            if (connection.isValid(5)) System.out.println("DB connected successfully");
            else throw new RuntimeException("Failed connection to DB");
            connection.close();
        } catch (SQLException e) {
            System.err.println(e.getMessage());
        }
    }
}
