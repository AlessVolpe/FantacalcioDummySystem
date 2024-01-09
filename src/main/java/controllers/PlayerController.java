package controllers;

import database.databaseDriver;
import models.FantaManager;
import org.jetbrains.annotations.NotNull;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

@SuppressWarnings("SqlSourceToSinkFlow")
public class PlayerController {
    private static void createPlayersTable(String connectionString) throws SQLException {
        Connection connection = DriverManager.getConnection(connectionString);
        if (!databaseDriver.doesTableExists(connection, "team")) {
            connection.close();
            throw new SQLException("Related table TEAM does not exist");
        }
        String[] columns = new String[]{
                "player_ID INTEGER AUTOINCREMENT",
                "player_name CHAR(50) NOT NULL",
                "player_email CHAR(100) NOT NULL",
                "player_password CHAR(255) NOT NULL",
                "player_fantateamID INT"};
        String[] constraints = new String[]{"PRIMARY KEY (player_ID), FOREIGN KEY (player_fantateam) REFERENCES TEAM (team_ID)"};
        database.databaseDriver.createTable(connectionString, "athlete", columns, constraints);
    }

    public static void addPlayerToDb(String connectionString, @NotNull FantaManager manager) {
        StringBuilder sql = new StringBuilder("INSERT INTO PLAYER (player_name, player_email, player_password) VALUES (");

        try (Connection connection = DriverManager.getConnection(connectionString);
             Statement statement = connection.createStatement()) {
            createPlayersTable(connectionString);
            if (!databaseDriver.isTableEmpty(statement, "player")) throw new SQLException("PLAYER table isn't empty");
            sql.append(manager.getName()).append(", ").append(manager.getEmail()).append(", ").append(manager.getPassword()).append(");");
            statement.executeUpdate(sql.toString());
        } catch (SQLException e) {
            System.err.println(e.getMessage());
        }
    }
}
