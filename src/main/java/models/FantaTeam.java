package models;

import java.util.LinkedList;
import java.util.Random;

import gameLogic.Rules;

public class FantaTeam {
    //#region properties
    private String name;
    public String getName() {
        return name;
    }

    private final String fantaManager;
    public String getFantaManager() {
        return fantaManager;
    }

    public void setName(String name) {
        this.name = name;
    }

    private String module;
    public String getModule() {
        return module;
    }

    public void setModule(String module) {
        Rules rules = new Rules();
        if (module != null && rules.getModules().contains(module)) {
            this.module = module;
        } else {
            Random random = new Random();
            this.module = rules.getModules().get(random.nextInt(rules.getModules().size()));
        }
    }

    private LinkedList<Goalkeeper> goalkeepers;
    public LinkedList<Goalkeeper> getGoalkeepers() {
        return goalkeepers;
    }

    private LinkedList<Player> players;
    public LinkedList<Player> getPlayers() {
        return players;
    }
    //#endregion

    //#region constructors
    public FantaTeam(String name, String fantaManager) {
        this.name = name;
        this.fantaManager = fantaManager;
        this.players = new LinkedList<>();
        this.goalkeepers = new LinkedList<>();
    }
    //#endregion

    //#region methods
    public void addPlayer(Player player) {
        if (player.getClass() == Goalkeeper.class) {
            addGoalkeeper((Goalkeeper) player); // If it doesn't work find the GK object with the same id
            return;
        }

        if (players == null) {
            players = new LinkedList<>();
        }
        players.add(player);
    }

    public void removePlayer(Player player) {
        if (player.getClass() == Goalkeeper.class) {
            removeGoalkeeper((Goalkeeper) player); // If it doesn't work find the GK object with the same id
            return;
        }

        if (players != null) {
            players.remove(player);
        }
    }

    private void addGoalkeeper(Goalkeeper goalkeeper) {
        if (goalkeepers == null) {
            goalkeepers = new LinkedList<>();
        }
        goalkeepers.add(goalkeeper);
    }

    private void removeGoalkeeper(Goalkeeper goalkeeper) {
        if (goalkeepers != null) {
            goalkeepers.remove(goalkeeper);
        }
    }
    //#endregion
}
