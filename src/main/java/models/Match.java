package models;

import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

import gameLogic.Rules;
import models.playerAttributes.PlayerStatus;
import models.playerAttributes.Position;
import org.jetbrains.annotations.NotNull;

public class Match {
    //#region properties
    private FantaTeam homeTeam;
    public FantaTeam getHomeTeam() {
        return homeTeam;
    }
    public void setHomeTeam(FantaTeam homeTeam) {
        this.homeTeam = homeTeam;
    }

    private FantaTeam awayTeam;
    public FantaTeam getAwayTeam() {
        return awayTeam;
    }
    public void setAwayTeam(FantaTeam awayTeam) {
        this.awayTeam = awayTeam;
    }

    private int homeTeamPoints;
    public int getHomeTeamPoints() {
        return homeTeamPoints;
    }

    public void setHomeTeamPoints(int homeTeamPoints) {
        this.homeTeamPoints = homeTeamPoints;
    }

    private int awayTeamPoints;
    public int getAwayTeamPoints() {
        return awayTeamPoints;
    }

    public void setAwayTeamPoints(int awayTeamPoints) {
        this.awayTeamPoints = awayTeamPoints;
    }

    private int homeTeamGoals;
    public int getHomeTeamGoals() {
        return homeTeamGoals;
    }

    public void setHomeTeamGoals(int homeTeamGoals) {
        this.homeTeamGoals = homeTeamGoals;
    }

    private int awayTeamGoals;
    public int getAwayTeamGoals() {
        return awayTeamGoals;
    }

    public void setAwayTeamGoals(int awayTeamGoals) {
        this.awayTeamGoals = awayTeamGoals;
    }

    private Rules rules;
    public Rules getRules() {
        return rules;
    }

    public void setRules(Rules rules) {
        this.rules = rules;
    }
    //#endregion

    //#region constructors
    public Match(FantaTeam homeTeam, FantaTeam awayTeam, Rules rules) {
        this.homeTeam = homeTeam;
        this.awayTeam = awayTeam;
        this.rules = rules;
    }
    //#endregion

    //#region public Methods
    public void calculatePoints() {
        calculatePoints(this.homeTeam);
        calculatePoints(this.awayTeam);
    }

    public void calculateGoals() {
        calculateGoals(this.homeTeam, this.rules);
        calculateGoals(this.awayTeam, this.rules);
    }
    //#endregion

    //#region private Methods
    private void calculatePoints(@NotNull FantaTeam team) {
        if (Objects.equals(team.getName(), this.homeTeam.getName())) {
            for (Goalkeeper goalkeeper : this.homeTeam.getGoalkeepers()) {
                if (goalkeeper.getPosition() == Position.GK && goalkeeper.getStatus() == PlayerStatus.FIRST_TEAM && goalkeeper.getGrade() != 0)
                    this.homeTeamPoints += goalkeeper.calculateFantaPoints();
                else if (goalkeeper.getStatus() == PlayerStatus.BENCH) this.homeTeamPoints += goalkeeper.calculateFantaPoints();
            }

        } else {
            for (Goalkeeper goalkeeper : this.awayTeam.getGoalkeepers()) {
                if (goalkeeper.getPosition() == Position.GK && goalkeeper.getStatus() == PlayerStatus.FIRST_TEAM && goalkeeper.getGrade() != 0)
                    this.awayTeamPoints += goalkeeper.calculateFantaPoints();
                else if (goalkeeper.getStatus() == PlayerStatus.BENCH) this.awayTeamPoints += goalkeeper.calculateFantaPoints();
            }

        }
        calculatePointsPerPosition(Position.DF, team);
        calculatePointsPerPosition(Position.MF, team);
        calculatePointsPerPosition(Position.FW, team);
    }

    private void calculateGoals(@NotNull FantaTeam team, Rules rules) {
        if (Objects.equals(team.getName(), this.homeTeam.getName())) {
            if (this.homeTeamPoints < rules.getMinPointsForGoal()) this.homeTeamGoals = 0;
            else if (this.homeTeamPoints == rules.getMinPointsForGoal()) this.homeTeamGoals = 1;
            else this.homeTeamGoals = 1 + (Math.round((float) (this.homeTeamPoints - rules.getMinPointsForGoal()) / rules.getGoalThreshold()));
        } else {
            if (this.homeTeamPoints < rules.getMinPointsForGoal()) this.awayTeamGoals = 0;
            else if (this.awayTeamPoints == rules.getMinPointsForGoal()) this.awayTeamGoals = 1;
            else this.awayTeamGoals = 1 + (Math.round((float) (this.awayTeamPoints - rules.getMinPointsForGoal()) / rules.getGoalThreshold()));
        }
    }

    private void calculatePointsPerPosition(Position position, @NotNull FantaTeam team) {
        List<Player> playersPerPosition = team
                .getPlayers()
                .stream()
                .filter(player -> player.getPosition() == position && player.getStatus() == PlayerStatus.FIRST_TEAM)
                .collect(Collectors.toList());

        for (Player player : playersPerPosition) {
            if (this.homeTeam.getPlayers().contains(player)) {
                this.homeTeamPoints += player.calculateFantaPoints();
            } else {
                this.awayTeamPoints += player.calculateFantaPoints();
            }
        }

        calculateSubsPoints(playersPerPosition, position, team);
    }

    private void calculateSubsPoints(List<Player> playersPerPosition, Position position, @NotNull FantaTeam team) {
        String[] module = team.getModule().split("-");

        if (Objects.equals(team.getName(), this.homeTeam.getName()) &&
                (playersPerPosition.stream().anyMatch(player -> player.getGrade() == 0)
                        || playersPerPosition.size() < Integer.parseInt(module[0]))) {
            this.homeTeamPoints += team
                    .getPlayers()
                    .stream()
                    .filter(player -> player.getStatus() == PlayerStatus.BENCH && player.getPosition() == position)
                    .findFirst()
                    .get()
                    .calculateFantaPoints();
        } else {
            this.awayTeamPoints += team
                    .getPlayers()
                    .stream()
                    .filter(player -> player.getStatus() == PlayerStatus.BENCH && player.getPosition() == position)
                    .findFirst()
                    .get()
                    .calculateFantaPoints();
        }
    }
}
//#endregion

