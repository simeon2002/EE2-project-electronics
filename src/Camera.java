import org.json.JSONArray;
import org.json.JSONObject;

import javax.imageio.ImageIO;
import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class Camera {

    private static JLabel cameraView;
    DBR dbr;

    //Singleton
    private static Camera instance;

    // Private constructor so it cannot be instantiated outside of this class
    private Camera() {
        // initialization code here
        dbr = new DBR();
    }

    // Public static method that returns the single instance of the class
    public static Camera getInstance() {
        // If the instance doesn't exist, create it
        if (instance == null) {
            // Synchronize block to remove multi-threading issues
            synchronized (Camera.class) {
                // Double check
                if (instance == null) {
                    instance = new Camera();
                }
            }
        }
        return instance;
    }


    public void setCameraView(JLabel cameraViewTemp){
        cameraView = cameraViewTemp;
    }

    public void updateCamera(String direction, int cameraID){
        String response = dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/get_servo_values/" + cameraID);
        JSONArray jsonArray = new JSONArray(response);
        JSONObject jsonObject = jsonArray.getJSONObject(0);

        int alpha = jsonObject.getInt("alpha");
        int beta = jsonObject.getInt("beta");
        int change = 15;

        switch (direction) {
            case "up" -> beta -= change;
            case "right" -> alpha -= change;
            case "down" -> beta += change;
            case "left" -> alpha += change;
            default -> {}
        }

        dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/insert_servo_values/" + cameraID + "/" + alpha + "/" + beta);
    }

    // stream
    public void setupStream(String tempMjpegUrl){
        String mjpegUrl = tempMjpegUrl;
        noStream();

        SwingWorker<Void, Void> worker = new SwingWorker<Void, Void>() {
            @Override
            protected Void doInBackground() throws Exception {
                captureFramesFromStream(mjpegUrl);
                return null;
            }
        };
        worker.execute();
    }
    private static void captureFramesFromStream(String mjpegUrl) {
         // Delay between retries in milliseconds (5 seconds)

        try {
            URL url = new URL(mjpegUrl);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");

            InputStream inputStream = connection.getInputStream();
            byte[] buffer = new byte[100000];
            int bytesRead;

            while ((bytesRead = inputStream.read(buffer)) > 0) {
                processMJPEGFrame(buffer, bytesRead);
            }

            inputStream.close();
            connection.disconnect();
        } catch (IOException e) {
            noStream();
            e.printStackTrace();
        }
    }
    private static void processMJPEGFrame(byte[] buffer, int bytesRead) {
        try {
            Thread.sleep(60);
            int startIndex = findStartOfJPEG(buffer, bytesRead);
            if (startIndex != -1) {
                int jpegDataLength = bytesRead - startIndex;
                byte[] jpegData = new byte[jpegDataLength];
                System.arraycopy(buffer, startIndex, jpegData, 0, jpegDataLength);

                BufferedImage image = ImageIO.read(new ByteArrayInputStream(jpegData));

                updateUI(image);
            }
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }
    private static int findStartOfJPEG(byte[] buffer, int bytesRead) {
        for (int i = 0; i < bytesRead - 1; i++) {
            if (buffer[i] == (byte) 0xFF && buffer[i + 1] == (byte) 0xD8) {
                return i;
            }
        }
        return -1;
    }
    private static void updateUI(BufferedImage image) {
        SwingUtilities.invokeLater(() -> {
            if (image != null) {
                Image scaledImage = image.getScaledInstance(cameraView.getWidth(), cameraView.getHeight(), Image.SCALE_SMOOTH);
                ImageIcon icon = new ImageIcon(scaledImage);
                cameraView.setIcon(icon);
            }
        });
    }

    private static void noStream(){
        SwingUtilities.invokeLater(() -> {
            cameraView.setFont(new Font("Arial", Font.BOLD, 30));
            cameraView.setForeground(Color.white);
            cameraView.setHorizontalAlignment(JLabel.CENTER);
            cameraView.setVerticalAlignment(JLabel.CENTER);
            cameraView.setText("<html>No video</html>");
        });
    }
}
