package dataHandling;

import org.javatuples.Triplet;
import org.jetbrains.annotations.NotNull;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

import java.util.HashMap;
import java.util.Map;

public class CSVReader {
    public static @NotNull Map<Integer, Triplet<String, String, String>> byBufferedReader(String filePath, DupKeyOption dupKeyOption) {
        String line;
        HashMap<Integer, Triplet<String, String, String>> outputMap = new HashMap<>();

        try(BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            reader.readLine(); // eats the header line that labels the records
            while ((line = reader.readLine()) != null) {
                String[] keyValuePair = line.split(",", 4);

                if (keyValuePair.length > 1) {
                    Integer key = Integer.parseInt(keyValuePair[0]);
                    Triplet<String, String, String> value = new Triplet<>(keyValuePair[1], keyValuePair[2], keyValuePair[3]);

                    if (DupKeyOption.OVERWRITE == dupKeyOption) outputMap.put(key, value);
                    else if (DupKeyOption.DISCARD == dupKeyOption) outputMap.putIfAbsent(key, value);
                } else {
                    System.out.println("No Key,Value found in line, ignoring: " + line);
                }
            }
        } catch (IOException e) {
            System.err.println(e.getMessage());
        }
        return outputMap;
    }
}