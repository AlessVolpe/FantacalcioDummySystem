package models.playerAttributes;

public enum Position {
    GK, DF, MF, FW;

    public String toString() {
        return switch (this) {
            case GK -> "Goalkeeper";
            case DF -> "Defender";
            case MF -> "Midfielder";
            case FW -> "Forward";
            default -> null;
        };
    }
}
