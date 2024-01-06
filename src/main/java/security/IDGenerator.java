package security;

import java.util.UUID;

public class IDGenerator {

    public static String randomStringUUID() {
        return UUID.randomUUID().toString();
    }
}