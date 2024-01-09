package security;

import org.jetbrains.annotations.NotNull;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class MD5Hashing {
    public String encrypt(@NotNull String plainText) {
        String cypherText = null;
        try {
            MessageDigest message = MessageDigest.getInstance("MD5");
            message.update(plainText.getBytes());

            byte[] bytes = message.digest();
            StringBuilder hash = new StringBuilder();
            for(byte b : bytes) {
                hash.append(Integer.toString((b & 0xff) + 0x100, 16).substring(1));
            }
            cypherText = hash.toString();
        } catch (NoSuchAlgorithmException e) {
            System.err.println(e.getMessage());
        }
        return cypherText;
    }
}
