package gameLogic;

import java.io.IOException;
import java.util.Scanner;

import org.jetbrains.annotations.NotNull;
import terminalToolkit.CLS;

public class Menu {
    public static int mainMenu(@NotNull Scanner scanner) throws InterruptedException, IOException {
        System.out.println("Hello, Fantamanagers!");
        System.out.println("Do you want to play with basic rules or with home rules?");
        System.out.println("1 - Basic rules");
        System.out.println("2 - Home rules");
        System.out.println("3 - Exit");

        int choice = scanner.nextInt();
        CLS.clearScreen();

        return choice;
    }
}
