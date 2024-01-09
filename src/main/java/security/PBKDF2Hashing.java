package security;

import org.jetbrains.annotations.NotNull;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.KeySpec;
import java.util.Arrays;
import java.util.Base64;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class PBKDF2Hashing {
    public static final String ID = "$31$";
    public static final int DEFAULT_COST = 16;
    private static final String ALGORITHM = "PBKDF2WithHmacSHA1";
    private static final int SIZE = 128;

    private final int cost;
    private final SecureRandom random;
    private static final Pattern layout = Pattern.compile("\\$31\\$(\\d\\d?)\\$(.{43})");

    public PBKDF2Hashing() {
        this(DEFAULT_COST);
    }

    public PBKDF2Hashing(int cost) {
        final int iterations = iterations(cost);
        this.cost = cost;
        this.random = new SecureRandom();
    }

    private static int iterations(int cost) {
        if ((cost < 0) || (cost > 30)) throw new IllegalArgumentException("cost: " + cost);
        return 1 << cost;
    }

    public @NotNull String hash(char[] plainText) {
        byte[] salt = new byte[SIZE / 8];
        random.nextBytes(salt);

        byte[] dk = pbkdf2(plainText, salt, 1 << cost);
        byte[] hash = new byte[salt.length + dk.length];
        System.arraycopy(salt, 0, hash, 0, salt.length);
        System.arraycopy(dk, 0, hash, salt.length, dk.length);

        Base64.Encoder encoder = Base64.getUrlEncoder().withoutPadding();
        return ID + cost + '$' + encoder.encodeToString(hash);
    }

    public boolean checkPassword(char[] password, String token) {
        Matcher matcher = layout.matcher(token);
        if (!matcher.matches()) throw new IllegalArgumentException("Invalid token format");

        int iterations = iterations(Integer.parseInt(matcher.group(1)));
        byte[] hash = Base64.getUrlDecoder().decode(matcher.group(2));
        byte[] salt = Arrays.copyOfRange(hash, 0, SIZE / 8);
        byte[] check = pbkdf2(password, salt, iterations);

        int zero = 0;
        for (int idx = 0; idx < check.length; ++idx) zero |= hash[salt.length + idx] ^ check[idx];
        return zero == 0;
    }

    private byte[] pbkdf2(char[] plainText, byte[] salt, int iterations) {
        byte[] kd = null;
        KeySpec spec = new PBEKeySpec(plainText, salt, iterations, SIZE);

        try {
            SecretKeyFactory keyFactory = SecretKeyFactory.getInstance(ALGORITHM);
            kd = keyFactory.generateSecret(spec).getEncoded();
        } catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
            System.err.println(e.getMessage());
        }
        return kd;
    }
}
