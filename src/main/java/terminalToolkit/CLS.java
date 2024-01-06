package terminalToolkit;

import java.io.IOException;

public class CLS {
    public static void clearScreen() throws InterruptedException, IOException {
        System.out.print("\033[H\033[2J");
        System.out.flush();
        //Runtime.getRuntime().exec("cls");
        new ProcessBuilder("cmd", "/c", "cls").inheritIO().start().waitFor();
    }
}