package gameLogic;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Scanner;

import terminalToolkit.CLS;

public class Rules {
    //#region points
    private int pointsPerGoal;
    public int getPointsPerGoal() {
        return pointsPerGoal;
    }

    public void setPointsPerGoal(int pointsPerGoal) {
        this.pointsPerGoal = pointsPerGoal;
    }

    private int pointsPerAssist;
    public int getPointsPerAssist() {
        return pointsPerAssist;
    }

    public void setPointsPerAssist(int pointsPerAssist) {
        this.pointsPerAssist = pointsPerAssist;
    }

    private double pointsPerYellowCard;
    public double getPointsPerYellowCard() {
        return pointsPerYellowCard;
    }

    public void setPointsPerYellowCard(double pointsPerYellowCard) {
        this.pointsPerYellowCard = pointsPerYellowCard;
    }

    private int pointsPerRedCard;
    public int getPointsPerRedCard() {
        return pointsPerRedCard;
    }

    public void setPointsPerRedCard(int pointsPerRedCard) {
        this.pointsPerRedCard = pointsPerRedCard;
    }

    private int pointsPerCleanSheet;
    public int getPointsPerCleanSheet() {
        return pointsPerCleanSheet;
    }

    public void setPointsPerCleanSheet(int pointsPerCleanSheet) {
        this.pointsPerCleanSheet = pointsPerCleanSheet;
    }

    private int pointsPerGoalAgainst;
    public int getPointsPerGoalAgainst() {
        return pointsPerGoalAgainst;
    }

    public void setPointsPerGoalAgainst(int pointsPerGoalAgainst) {
        this.pointsPerGoalAgainst = pointsPerGoalAgainst;
    }

    private int pointsPerOwnGoal;
    public int getPointsPerOwnGoal() {
        return pointsPerOwnGoal;
    }

    public void setPointsPerOwnGoal(int pointsPerOwnGoal) {
        this.pointsPerOwnGoal = pointsPerOwnGoal;
    }

    private int pointsPerPenalty;
    public int getPointsPerPenalty() {
        return pointsPerPenalty;
    }

    public void setPointsPerPenalty(int pointsPerPenalty) {
        this.pointsPerPenalty = pointsPerPenalty;
    }

    private int pointsPerPenaltySaved;
    public int getPointsPerPenaltySaved() {
        return pointsPerPenaltySaved;
    }

    public void setPointsPerPenaltySaved(int pointsPerPenaltySaved) {
        this.pointsPerPenaltySaved = pointsPerPenaltySaved;
    }
    //#endregion

    //#region configuration
    private ArrayList<String> modules = new ArrayList<>();
    public ArrayList<String> getModules() {
        return modules;
    }

    public void setModules(ArrayList<String> modules) {
        this.modules = modules;
    }

    private int minPlayedMinutes;
    public int getMinPlayedMinutes() {
        return minPlayedMinutes;
    }

    public void setMinPlayedMinutes(int minPlayedMinutes) {
        this.minPlayedMinutes = minPlayedMinutes;
    }

    private int minPointsForGoal;
    public int getMinPointsForGoal() {
        return minPointsForGoal;
    }

    public void setMinPointsForGoal(int minPointsForGoal) {
        this.minPointsForGoal = minPointsForGoal;
    }

    private int goalThreshold;
    public int getGoalThreshold() {
        return goalThreshold;
    }

    public void setGoalThreshold(int goalThreshold) {
        this.goalThreshold = goalThreshold;
    }
    //#endregion

    //#region constructors
    public Rules() {
        this.pointsPerGoal = 3;
        this.pointsPerAssist = 1;
        this.pointsPerYellowCard = 0.5;
        this.pointsPerRedCard = 1;
        this.pointsPerCleanSheet = 1;
        this.pointsPerGoalAgainst = 1;
        this.pointsPerOwnGoal = 3;
        this.pointsPerPenalty = 3;
        this.pointsPerPenaltySaved = 3;
        this.minPlayedMinutes = 10;
        this.minPointsForGoal = 66;
        this.goalThreshold = 4;
        this.modules.addAll(Arrays.asList("4-4-2", "3-5-2", "4-3-3", "3-4-3", "5-3-2", "4-5-1", "5-4-1"));
    }

    public Rules(int pointsPerGoal,
                 int pointsPerAssist,
                 double pointsPerYellowCard,
                 int pointsPerRedCard,
                 int pointsPerCleanSheet,
                 int pointsPerGoalAgainst,
                 int pointsPerOwnGoal,
                 int pointsPerPenalty,
                 int pointsPerPenaltySaved,
                 int minPlayedMinutes,
                 int minPointsForGoal,
                 int goalThreshold,
                 ArrayList<String> modules) {
        this.pointsPerGoal = pointsPerGoal;
        this.pointsPerAssist = pointsPerAssist;
        this.pointsPerYellowCard = pointsPerYellowCard;
        this.pointsPerRedCard = pointsPerRedCard;
        this.pointsPerCleanSheet = pointsPerCleanSheet;
        this.pointsPerGoalAgainst = pointsPerGoalAgainst;
        this.pointsPerOwnGoal = pointsPerOwnGoal;
        this.pointsPerPenalty = pointsPerPenalty;
        this.pointsPerPenaltySaved = pointsPerPenaltySaved;
        this.minPlayedMinutes = minPlayedMinutes;
        this.minPointsForGoal = minPointsForGoal;
        this.goalThreshold = goalThreshold;
        this.modules.addAll(modules);
    }
    //#endregion

    public static Rules setRules(int choice, Scanner scanner) throws InterruptedException, IOException {
        Rules rules = null;

        switch (choice) {
            case 1:
                System.out.println("You've chosen basic rules");
                rules = new Rules();
                break;
            case 2:
                System.out.println("You've chosen basic rules");

                System.out.println("Enter points per goals: ");
                int goals = scanner.nextInt();
                System.out.println("Enter points per assists: ");
                int assists = scanner.nextInt();
                System.out.println("Enter points per yellow card: ");
                double yellow = scanner.nextDouble();
                System.out.println("Enter points per red card: ");
                int red = scanner.nextInt();
                System.out.println("Enter points per clean sheet: ");
                int clean = scanner.nextInt();
                System.out.println("Enter points per goal against: ");
                int goalAgainst = scanner.nextInt();
                System.out.println("Enter points per own goal: ");
                int ownGoal = scanner.nextInt();
                System.out.println("Enter points per penalty: ");
                int penalty = scanner.nextInt();
                System.out.println("Enter points per penalty saved: ");
                int saved = scanner.nextInt();

                System.out.println("Enter minimum minutes to get a grade: ");
                int minutes = scanner.nextInt();
                System.out.println("Enter minimum points to score a goal: ");
                int points = scanner.nextInt();
                System.out.println("Enter goal threshold: ");
                int threshold = scanner.nextInt();

                System.out.println("As a proof of concept, we'll provide a list of modules.");
                ArrayList<String> modules = new ArrayList<>(Arrays.asList("4-4-2", "3-5-2", "4-3-3", "3-4-3", "5-3-2", "4-5-1", "5-4-1"));

                rules = new Rules(goals, assists, yellow, red, clean, goalAgainst, ownGoal, penalty, saved, minutes, points, threshold, modules);
                break;
            case 3:
                System.out.println("Exit");
            default:
                System.exit(0);
        }

        CLS.clearScreen();
        return rules;
    }
}
