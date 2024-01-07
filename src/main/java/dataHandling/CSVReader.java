package dataHandling;

import org.javatuples.Triplet;
import org.jetbrains.annotations.NotNull;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Scanner;

public class CSVReader {
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

    @SuppressWarnings("MismatchedQueryAndUpdateOfCollection")
    public static void reader(String filePath) {
        List<List<String>> records = new LinkedList<>();
        try (Scanner scanner = new Scanner(new File(filePath))) {
            while (scanner.hasNextLine()) {
                records.add(getRecordFromLine(scanner.nextLine()));
            }
        } catch (Exception e) {
            System.err.println(e.getMessage());
        }
    }

    private static @NotNull List<String> getRecordFromLine(String line) {
        List<String> values = new LinkedList<>();
        try (Scanner rowScanner = new Scanner(line)) {
            rowScanner.useDelimiter(",");
            while (rowScanner.hasNext()) {
                values.add(rowScanner.next());
            }
        } catch (Exception e) {
            System.err.println(e.getMessage());
        }
        return values;
    }
}