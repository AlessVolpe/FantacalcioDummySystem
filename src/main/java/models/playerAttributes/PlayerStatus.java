package models.playerAttributes;

public enum PlayerStatus {
    FIRST_TEAM, BENCH, STANDS;

    public String toString() {
        return switch (this) {
            case FIRST_TEAM -> "First Team";
            case BENCH -> "Bench";
            case STANDS -> "Stands";
            default -> null;
        };
    }
}
