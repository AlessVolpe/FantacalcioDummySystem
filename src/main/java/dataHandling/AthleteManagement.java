package dataHandling;

import java.io.*;
import java.util.*;

import org.javatuples.Triplet;
import org.jetbrains.annotations.NotNull;

public class AthleteManagement {
    public static @NotNull Map<Integer, Triplet<String, String, String>> byBufferedReader(String filePath, DupKeyOption dupKeyOption) {
        String line;
        HashMap<Integer, Triplet<String, String, String>> outputMap = new HashMap<>();

        try(BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String headerLine = reader.readLine(); // eats the header line that labels the records
            while ((line = reader.readLine()) != null) {
                String[] keyValuePair = line.split(",", 4);

                if (keyValuePair.length > 1) {
                    Integer key = Integer.parseInt(keyValuePair[0]);
                    Triplet<String, String, String> value = new Triplet<>(keyValuePair[1], keyValuePair[2], keyValuePair[3]);

                    if (DupKeyOption.OVERWRITE == dupKeyOption) outputMap.put(key, value);
                    else outputMap.putIfAbsent(key, value);
                } else {
                    System.out.println("No Key,Value found in line, ignoring: " + line);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return outputMap;
    }

    public static void athletesToDB(@NotNull Map<Integer, Triplet<String, String, String>> unpackedAthletes) {
        return;
    }
}
