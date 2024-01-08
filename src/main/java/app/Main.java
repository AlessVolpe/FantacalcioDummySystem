package app;

import java.io.IOException;
import java.util.ResourceBundle;
import java.util.Scanner;

import gameLogic.*;

public class Main {
    public static void main(String[] args) throws IOException, InterruptedException {
        ResourceBundle appProperties = StartSequence.propertyLoader();
        String connectionString = appProperties.getString("db.url");
        StartSequence.testDBConnection(connectionString);

        // Game configuration
        Scanner scanner = new Scanner(System.in);
        int choice = Menu.mainMenu(scanner);
        Rules rules = Rules.setRules(choice, scanner);

        try {
            PlayerManagement.addPlayers(scanner);
        } catch (Exception e) {
            System.err.println(e.getMessage());
        }

        // Play
        if (rules != null) {
            try {
                Game.play(rules);
            } catch (Exception e) {
                System.err.println(e.getMessage());
            }
        }
        scanner.close();
    }
}