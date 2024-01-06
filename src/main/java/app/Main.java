package app;

import java.io.IOException;
import java.util.Scanner;

import gameLogic.*;

public class Main {
    public static void main(String[] args) throws IOException, InterruptedException {
        Scanner scanner = new Scanner(System.in);

        // Game configuration
        int choice = Menu.mainMenu(scanner);
        Rules rules = Rules.setRules(choice, scanner);

        try {
            PlayerManagement.addPlayers(scanner);
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("Error: " + e);
        }

        // Play
        if (rules != null) {
            try {
                GameGame.play(rules);
            } catch (Exception e) {
                System.out.println("Error: " + e);
            }
        }
        scanner.close();
    }
}