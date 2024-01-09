package controllers;

import java.io.IOException;
import java.util.Scanner;

import gameLogic.Game;
import models.FantaManager;
import terminalToolkit.CLS;
import dataHandling.EmailValidator;

public class PlayerController {
    public static void addPlayers(Scanner scanner) throws InterruptedException, IOException {
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

            FantaManager manager = new FantaManager(name, email);
            Game.addManager(manager);

            System.out.println("Manager " + name + " added!");
            CLS.clearScreen();
            i++;
        }
    }
}
