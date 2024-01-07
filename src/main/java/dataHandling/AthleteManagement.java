package dataHandling;

import java.util.LinkedList;

public class AthleteManagement {
    private static void createAthletesTable(String connectionString) {
        // Objects will be populated
        String[] columns = new String[] {};
        String[] constraints = new String[] {};
        database.databaseDriver.createTable(connectionString, "athletes", columns, constraints);
    }

    public static void addAthletesToDb(String connectionString, LinkedList<String> extractedPlayers) {
        createAthletesTable(connectionString);

        // add each and every player to the db
    }
}
