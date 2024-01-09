package app;

import controllers.PlayerController;
import dataHandling.EmailValidator;
import gameLogic.Game;
import models.FantaManager;
import org.jetbrains.annotations.NotNull;
import security.PBKDF2Hashing;
import terminalToolkit.CLS;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ResourceBundle;
import java.util.Scanner;

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

    public static void addPlayers(@NotNull Scanner scanner) throws InterruptedException, IOException {
        System.out.println("How many players do you want to play with?");
        int i = 0,
                managers = scanner.nextInt();
        scanner.nextLine(); // eats the \n character

        while (i < managers) {
            System.out.println("Enter player name: ");
            String name = scanner.nextLine();
            System.out.println("Enter player email: ");
            String email = scanner.nextLine();

            while (!(EmailValidator.emailPatternMatches(email) || EmailValidator.emailDNSLookup(email))) {
                System.out.println("Invalid email!");
                CLS.clearScreen();
                System.out.println("Enter a valid player email: ");
                email = scanner.nextLine();
            }

            System.out.println("Enter player password: ");
            String password = scanner.nextLine();
            PBKDF2Hashing hasher = new PBKDF2Hashing();
            password = hasher.hash(password.toCharArray());

            FantaManager manager = new FantaManager(name, email, password);
            Game.addManager(manager);
            PlayerController.addPlayerToDb(propertyLoader().getString("db.url"), manager);

            System.out.println("Manager " + name + " added!");
            CLS.clearScreen();
            i++;
        }
    }
}
