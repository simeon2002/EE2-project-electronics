import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Random;

public class RandomTemperatureToDB {
    public static void main(String[] args) throws UnsupportedEncodingException {
        DBR dbr = new DBR();
        String response = "";

        Random random = new Random();
        int maxT = 40;
        int minT = 37;
        int temperature;

        String date;
        String urlDate;

        String values;
        String url;

        LocalDateTime startDateTime;
        LocalDateTime staDateTime = LocalDateTime.of(2024, 3, 27, 12, 0, 0);
        LocalDateTime endDateTime = LocalDateTime.of(2024, 3, 27, 12, 0, 0);
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

        for (int horseID = 1; horseID <= 25; horseID++) {
            startDateTime  = staDateTime;
            while (startDateTime.isBefore(endDateTime) || startDateTime.isEqual(endDateTime)) {
                temperature = random.nextInt((maxT - minT) + 1) + minT;

                date = startDateTime.format(formatter);
                try {
                    urlDate = URLEncoder.encode(date, StandardCharsets.UTF_8.toString());
                } catch (UnsupportedEncodingException e) {
                    throw new RuntimeException(e);
                }

                values = temperature + "/" + urlDate + "/" + horseID;
                url = "https://studev.groept.be/api/a23ib2d03/insert_temperature_2/" + values;
                response = dbr.makeGETRequest(url);
                System.out.println(horseID + " : " + response +  " : " + url);
                startDateTime = startDateTime.plusMinutes(1);
            }
        }
    }
}