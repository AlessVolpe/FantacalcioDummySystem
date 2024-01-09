package security;

import org.jetbrains.annotations.NotNull;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class SHA256Hashing {
    private static byte[] getSHA(@NotNull String input) throws NoSuchAlgorithmException {
        MessageDigest message = MessageDigest.getInstance("SHA-256");
        return message.digest(input.getBytes(StandardCharsets.UTF_8));
    }

    private static @NotNull String toHexString(byte[] hash) {
        BigInteger number = new BigInteger(1, hash);
        StringBuilder hexString = new StringBuilder(number.toString(16));

        while (hexString.length() < 32) hexString.insert(0, '0');
        return hexString.toString();
    }

    public static String encrypt(String plainText) {
        String cypherText = null;
        try {
            cypherText = toHexString(getSHA(plainText));
        } catch (NoSuchAlgorithmException e) {
            System.err.println(e.getMessage());
        }
        return cypherText;
    }
}
