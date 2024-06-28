import org.json.JSONArray;
import org.json.JSONObject;

import javax.swing.*;

public class main {
    public static void main(String[] args) {
        DBR dbr = new DBR();

        String response = dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/get_camera_ip/1");
        JSONArray jsonArray = new JSONArray(response);
        JSONObject jsonObject = jsonArray.getJSONObject(0);
        String ip = jsonObject.getString("cameraIP");
        String port = "8000";

        String mjpegUrl = "http://" + ip + ":" + port + "/stream.mjpg";
        SwingUtilities.invokeLater(() ->
        {
            Camera camera = Camera.getInstance();
            camera.setupStream(mjpegUrl);

            new SplashScreen();


        });
    }
}
