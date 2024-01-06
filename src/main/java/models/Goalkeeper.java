package models;

import gameLogic.Rules;
import models.playerAttributes.Position;
import org.jetbrains.annotations.NotNull;

public class Goalkeeper extends Athlete {
    //#region properties
    private int goalsAgainst;
    public int getGoalsAgainst() {
        return goalsAgainst;
    }

    public void setGoalsAgainst(int goalsAgainst) {
        this.goalsAgainst = goalsAgainst;
    }

    private boolean hasSavedPenalty;
    public boolean isHasSavedPenalty() {
        return hasSavedPenalty;
    }

    public void setHasSavedPenalty(boolean hasSavedPenalty) {
        this.hasSavedPenalty = hasSavedPenalty;
    }
    //#endregion

    //#region constructor
    public Goalkeeper(int id, String Name, String Team, @NotNull Position Position) {
        super(id, Name, Team, Position);
    }
    //#endregion

    //#region methods
    @Override
    public int calculateFantaPoints() {
        Rules rules = new Rules();
        super.calculateFantaPoints();

        // Clean sheet
        if (this.goalsAgainst == 0) this.setFantaPoints(this.getFantaPoints() + rules.getPointsPerCleanSheet());
        else this.setFantaPoints(this.getFantaPoints() - this.goalsAgainst * rules.getPointsPerGoalAgainst());

        // Saved penalty
        if (this.isHasSavedPenalty()) this.setFantaPoints(this.getFantaPoints() + rules.getPointsPerPenaltySaved());

        return this.getFantaPoints();
    }
    //#endregion
}
