package dataHandling;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class CSVReader {
    public static void reader(String filePath) {
        List<List<String>> records = new ArrayList<>();
        try (Scanner scanner = new Scanner(new File(filePath))) {
            while (scanner.hasNextLine()) {
                records.add(getRecordFromLine(scanner.nextLine()));
            }
        } catch (Exception e) {
            System.out.println("Error in CsvFileReader!");
            e.printStackTrace();
        }
    }

    private static List<String> getRecordFromLine(String line) {
        List<String> values = new ArrayList<>();
        try (Scanner rowScanner = new Scanner(line)) {
            rowScanner.useDelimiter(",");
            while (rowScanner.hasNext()) {
                values.add(rowScanner.next());
            }
        } catch (Exception e) {
            System.out.println("Error in getRecordFromLine!");
            e.printStackTrace();
        }
        return values;
    }
}
