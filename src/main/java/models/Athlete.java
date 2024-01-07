package models;

import gameLogic.Rules;
import models.playerAttributes.PlayerStatus;
import models.playerAttributes.Position;
import org.jetbrains.annotations.NotNull;

public class Athlete {
    //#region properties
    private final int id;
    public int getId() {
        return id;
    }

    private final String name;
    public String getName() {
        return name;
    }

    private String team;
    public void setTeam(String team) {
        this.team = team;
    }

    public String getTeam() {
        return team;
    }

    private int jerseyNumber;
    public void setJerseyNumber(int jerseyNumber) {
        this.jerseyNumber = jerseyNumber;
    }

    public int getJerseyNumber() {
        return jerseyNumber;
    }

    private final Position position;
    public Position getPosition() {
        return position;
    }
    private PlayerStatus status;
    public PlayerStatus getStatus() {
        return status;
    }

    public void setStatus(PlayerStatus status) {
        this.status = status;
    }

    private int goals;
    public int getGoals() {
        return goals;
    }

    public void setGoals(int goals) {
        this.goals = goals;
    }

    private int assists;
    public int getAssists() {
        return assists;
    }

    public void setAssists(int assists) {
        this.assists = assists;
    }

    private int penaltyScored;
    public int getPenaltyScored() {
        return penaltyScored;
    }

    public void setPenaltyScored(int penaltyScored) {
        this.penaltyScored = penaltyScored;
    }

    private int penaltyMissed;
    public int getPenaltyMissed() {
        return penaltyMissed;
    }

    public void setPenaltyMissed(int penaltyMissed) {
        this.penaltyMissed = penaltyMissed;
    }

    private int ownGoals;
    public int getOwnGoals() {
        return ownGoals;
    }

    public void setOwnGoals(int ownGoals) {
        this.ownGoals = ownGoals;
    }

    private boolean yellowCard;
    public boolean getYellowCard() {
        return yellowCard;
    }

    public void setYellowCard(boolean yellowCard) {
        this.yellowCard = yellowCard;
    }

    private boolean redCard;
    public boolean getRedCard() {
        return redCard;
    }

    public void setRedCard(boolean redCard) {
        this.redCard = redCard;
    }

    private int minutesPlayed;
    public int getMinutesPlayed() {
        return minutesPlayed;
    }

    public void setMinutesPlayed(int minutesPlayed) {
        this.minutesPlayed = minutesPlayed;
    }

    private FantaTeam fantaTeam;
    public FantaTeam getFantaTeam() {
        return fantaTeam;
    }

    private int grade;
    public int getGrade() {
        return grade;
    }

    public void setGrade(int grade) {
        this.grade = grade;
    }

    private int fantaPoints;
    public int getFantaPoints() {
        return fantaPoints;
    }

    public void setFantaPoints(int fantaPoints) {
        this.fantaPoints = fantaPoints;
    }
    //#endregion

    //#region constructors
    public Athlete(int id, String name, String team, @NotNull Position position) {
        this.id = id;
        this.name = name;
        this.team = team;
        if (position.equals(Position.GK)) new Goalkeeper(id, name, team, position);
        this.position = position;
    }
    //#endregion

    //#region methods
    public void addToFantaTeam(@NotNull FantaTeam fantaTeam) {
        this.fantaTeam = fantaTeam;
        fantaTeam.addPlayer(this);
        System.out.println(this.name + " added to " + fantaTeam.getName());
    }

    public void removeFromFantaTeam() {
        String fantaTeamName = fantaTeam.getName();
        this.fantaTeam.removePlayer(this);
        this.fantaTeam = null;
        System.out.println(this.name + " removed from " + fantaTeamName);
    }

    public int calculateFantaPoints() {
        Rules rules = new Rules();

        if (this.minutesPlayed < rules.getMinPlayedMinutes()) {
            this.grade = 0;
            this.fantaPoints = 0;
            return this.fantaPoints;
        }

        // Bonus
        this.fantaPoints += this.goals * rules.getPointsPerGoal() + this.assists * rules.getPointsPerAssist();
        if (this.penaltyScored > 0) this.fantaPoints += rules.getPointsPerPenalty() * this.penaltyScored;

        // Malus
        if (this.yellowCard) this.fantaPoints -= (int) rules.getPointsPerYellowCard();
        if (this.redCard) this.fantaPoints -= rules.getPointsPerRedCard();
        if (this.penaltyMissed > 0) this.fantaPoints -= rules.getPointsPerPenalty() * this.penaltyMissed;
        if (this.ownGoals > 0) this.fantaPoints -= rules.getPointsPerOwnGoal() * this.ownGoals;

        return this.fantaPoints;
    }
    //#endregion
}
