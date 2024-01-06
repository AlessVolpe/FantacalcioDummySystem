package gameLogic;

import java.util.LinkedList;

import models.*;

public class Game {
    private static LinkedList<FantaManager> managers;
    public LinkedList<FantaManager> getManagers() {
        return managers;
    }

    public static void addManager(FantaManager manager) {
        if (managers == null)
            managers = new LinkedList<>();
        managers.add(manager);
    }

    public static void play(Rules rules) {
        for (FantaManager manager : managers) {
            System.out.println("Manager: " + manager.toString());
        }
    }
}
