import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.XYPlot;
import org.jfree.data.Range;
import org.jfree.data.time.Minute;
import org.jfree.data.time.TimeSeries;
import org.jfree.data.time.TimeSeriesCollection;
import org.json.JSONArray;
import org.json.JSONObject;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Map;
import java.util.TreeMap;
import java.util.List;

@SuppressWarnings("CallToPrintStackTrace")
public class HorseManagementHorsePage extends JFrame {

    private static JLabel cameraView;

    JScrollPane scrollPane;
    JPanel horseButtonPanel;
    JPanel alarmPanel;
    JPanel buttonPanel;
    JPanel sidePanel;
    JPanel mainPanel;
    JPanel cameraPanel;
    JPanel medicalInfoPanel;
    JPanel heartRatePanel;
    JPanel temperaturePanel;

    JSlider hoursBackSlider;
    JButton homeButton;

    Camera camera;
    DBR dbr;
    JSONArray horses;
    JSONObject horse;
    SimpleDateFormat dateFormat;

    boolean toggle;

    int horseID;
    int numberOfHorses;
    int sidePanelWidth = 300;
    int medicalPanelHeight = 300;
    int hoursBack = 1;

    long currentTimeMillis;
    long earliestTimeMillis;
    long latestDataTimeMillis;

    Color medicalInfoPanelColor;
    Color sidePanelColor;

    Timer timer1;
    Timer timer2;

    public HorseManagementHorsePage(int horseIDTemp) {
        dbr = new DBR();
        cameraView = new JLabel();
        camera = Camera.getInstance();
        horseID = horseIDTemp;
        dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

        medicalInfoPanelColor = Color.lightGray;
        sidePanelColor = Color.lightGray;

        updateHorses();

        Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
        setTitle(horse.getString("name"));
        setSize((int) screenSize.getWidth(), (int) screenSize.getHeight()); //chose size
        setExtendedState(JFrame.MAXIMIZED_BOTH); //fullscreen
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        medicalPanelHeight = getHeight()/4;
        sidePanelWidth = getWidth()/6;

        moveServoToHorse();

        initGUI();
        updateGUI(0);
        setVisible(true);

        startTimers();
    }

    private void startTimers(){
        //Every 10 seconds: alarm
        timer1 = new Timer(10000, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                try {
                    updateGUI(1);
                } catch (Exception ex) {
                    ex.printStackTrace();
                }
            }
        });
        timer1.start();

        //Every minute: scrollbar and graphs
        timer2 = new Timer(60000, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                try {
                    updateGUI(2);
                } catch (Exception ex) {
                    ex.printStackTrace();
                }
            }
        });
        timer2.start();
    }


    private void initGUI() {
        setLayout(new BorderLayout());
        camera.setCameraView(cameraView);

        horseButtonPanel = new JPanel(new GridLayout(0, 1));
        mainPanel = new JPanel(new BorderLayout());
        cameraPanel = new JPanel(new BorderLayout());
        cameraPanel.setBackground(Color.BLACK);
        scrollPane = new JScrollPane(horseButtonPanel);
        scrollPane.setPreferredSize(new Dimension(200, Integer.MAX_VALUE));
        alarmPanel = new JPanel(new GridLayout(0, 1));


        initSidePanel();
        initMedicalInfoPanel();

        cameraPanel.add(cameraView, BorderLayout.CENTER);
        add(sidePanel, BorderLayout.EAST);

        mainPanel.add(cameraPanel, BorderLayout.CENTER);
        mainPanel.add(medicalInfoPanel, BorderLayout.SOUTH);

        add(scrollPane, BorderLayout.WEST);
        add(mainPanel, BorderLayout.CENTER);
    }

    private void initButtons(){
        // Create buttons
        JButton upButton = new JButton("Up");
        JButton leftButton = new JButton("Left");
        JButton rightButton = new JButton("Right");
        JButton downButton = new JButton("Down");

        // Set  action listeners
        upButton.addActionListener(e -> {
            camera.updateCamera("up", 1);
        });
        leftButton.addActionListener(e -> {
            camera.updateCamera("left", 1);
        });
        rightButton.addActionListener(e -> {
            camera.updateCamera("right", 1);
        });
        downButton.addActionListener(e -> {
            camera.updateCamera("down", 1);
        });

        // Add buttons to the panel
        buttonPanel = new JPanel(new GridLayout(2, 3));
        buttonPanel.add(new JLabel(""));
        buttonPanel.add(upButton);
        buttonPanel.add(new JLabel(""));
        buttonPanel.add(leftButton);
        buttonPanel.add(downButton);
        buttonPanel.add(rightButton);
    }

    private void initSidePanel(){
        sidePanel = new JPanel(new GridLayout(3, 1)){
            @Override
            public Dimension getPreferredSize() {
                return new Dimension(sidePanelWidth, super.getPreferredSize().height); // Set desired height here
            }
        };

        homeButton = new JButton("Home");
        homeButton.setFont(new Font("Arial", Font.BOLD, 60));
        homeButton.setBackground(Color.decode("#1abc9c"));
        homeButton.addActionListener(e -> {
            SwingUtilities.invokeLater(HorseManagement::new);
            timer1.stop();
            timer2.stop();
            this.dispose();
        });

        initButtons();

        alarmPanel.setBackground(sidePanelColor);
        buttonPanel.setBackground(sidePanelColor);

        sidePanel.add(homeButton);
        sidePanel.add(alarmPanel);
        sidePanel.add(buttonPanel);
    }

    private void initMedicalInfoPanel(){
        medicalInfoPanel = new JPanel(new BorderLayout());

        hoursBackSlider = new JSlider(JSlider.HORIZONTAL, 1, 24, hoursBack);
        hoursBackSlider.setMajorTickSpacing(1); // Set major tick spacing
        hoursBackSlider.setMinorTickSpacing(1);  // Set minor tick spacing
        hoursBackSlider.setPaintTicks(true);     // Display tick marks
        hoursBackSlider.setPaintLabels(true);    // Display number labels on major ticks
        hoursBackSlider.addChangeListener(e -> {
            JSlider source = (JSlider)e.getSource();
            if (!source.getValueIsAdjusting()) {
                hoursBack = (int) source.getValue();
                updateGraphs();
            }
        });
        hoursBackSlider.setBorder(BorderFactory.createEmptyBorder(0, 10, 10, 10));

        temperaturePanel = new JPanel(new BorderLayout()) {
            @Override
            public Dimension getPreferredSize() {
                return new Dimension(super.getPreferredSize().width, medicalPanelHeight);
            }
        };
        heartRatePanel = new JPanel(new BorderLayout()) {
            @Override
            public Dimension getPreferredSize() {
                return new Dimension(super.getPreferredSize().width, medicalPanelHeight);
            }
        };

        hoursBackSlider.setBackground(medicalInfoPanelColor);
        temperaturePanel.setBackground(medicalInfoPanelColor);
        heartRatePanel.setBackground(medicalInfoPanelColor);

        medicalInfoPanel.add(temperaturePanel, BorderLayout.CENTER);
        medicalInfoPanel.add(hoursBackSlider, BorderLayout.SOUTH);
    }


    private void updateGUI(int n) {
        updateHorses();

        switch (n) {
            case 1:
                updateAlarms();
                break;
            case 2:
                updateGraphs();
                updateScrollPanel();
                break;
            default:
                updateAlarms();
                updateGraphs();
                updateScrollPanel();
                break;
        }
    }

    private void updateHorses(){
        horses = new JSONArray(dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/get_horses"));
        horse = (new JSONArray(dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/get_horse/" + horseID))).getJSONObject(0);
        numberOfHorses = horses.length();
    }

    private void updateScrollPanel(){
        horseButtonPanel.removeAll();
        updateHorses();

        for (int i = 0; i < numberOfHorses; i++) {
            JSONObject horse = horses.getJSONObject(i);
            int id = horse.getInt("horseID");
            String name = horse.getString("name");

            JButton horseButtonTemp = new JButton(name);
            horseButtonTemp.setFont(new Font("Arial", Font.BOLD, 25));
            horseButtonTemp.addActionListener(e -> {
                SwingUtilities.invokeLater(() -> new HorseManagementHorsePage(id));
                timer1.stop();
                timer2.stop();
                this.dispose();
            });
            horseButtonTemp.setBorder(BorderFactory.createCompoundBorder(horseButtonTemp.getBorder(), BorderFactory.createEmptyBorder(5, 0, 5, 0)));
            horseButtonPanel.add(horseButtonTemp);
        }

        horseButtonPanel.revalidate();
        horseButtonPanel.repaint();
    }

    private void updateAlarms() {
        alarmPanel.removeAll();

        //Check if there is an alarm on this horse
        //If so a button to turn the alarm off is shown
        int alarm = horse.getInt("alarm");
        if(alarm == 1){
            JButton jButton = new JButton("Turn alarm off");
            jButton.setBackground(Color.green);
            jButton.addActionListener(e -> {
                dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/turn_of_alarm/" + horseID);
                alarmPanel.remove(jButton);
                alarmPanel.revalidate();
                alarmPanel.repaint();
            });

            alarmPanel.add(jButton);
        }

        //Make the alarm button light up to indicate there is an alarm on another horse
        boolean thereIsAnAlarm = false;
        for (int i = 0; i < numberOfHorses; i++) {
            JSONObject horseTemp = horses.getJSONObject(i);
            if(horseTemp.getInt("alarm") == 1 && horse.getInt("horseID") != horseTemp.getInt("horseID")){
                thereIsAnAlarm = true;
                break;
            }
        }

        if(thereIsAnAlarm){
            toggle = !toggle;
            if(toggle) {
                homeButton.setBackground(Color.yellow);
            }else{
                homeButton.setBackground(Color.red);
            }
        }else{
            homeButton.setBackground(null);
        }

        alarmPanel.revalidate();
        alarmPanel.repaint();
    }

    private void updateGraphs(){
        updateTemperatureGraph();
        updateHeartRateGraph();
    }

    private void updateTemperatureGraph() {
        temperaturePanel.removeAll();

        JSONArray temperatures = new JSONArray(dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/get_temperature/" + horseID));

        //current time
        currentTimeMillis = System.currentTimeMillis();
        //earliest time in specified period
        earliestTimeMillis = currentTimeMillis - (hoursBack * 60L * 60L * 1000L);
        //time from latest datapoint
        try {
            latestDataTimeMillis = dateFormat.parse(temperatures.getJSONObject(0).getString("ts")).getTime();
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }

        //If there is no data for the specified time period
        if( latestDataTimeMillis < earliestTimeMillis){
            JLabel noData = new JLabel("No data", SwingConstants.CENTER);
            noData.setFont(new Font("Arial", Font.BOLD, 30));
            temperaturePanel.add(noData);
        }else {
            TimeSeries series = new TimeSeries("Temperature");
            calculateAndAddToSeries(temperatures, series, "temp");

            TimeSeriesCollection dataset = new TimeSeriesCollection();
            dataset.addSeries(series);

            String title = "Temperature of " + horse.getString("name") + " : " + getLatestValue(temperatures, "temp") + "°C";
            JFreeChart chart = ChartFactory.createTimeSeriesChart(
                    title,          // Title
                    "",             // X-Axis label
                    "",             // Y-Axis label
                    dataset,        // Dataset
                    false,          // Legend
                    true,           // Tooltips
                    false           // URLs
            );

            XYPlot plot = chart.getXYPlot();
            plot.getRangeAxis().setRange(new Range(36, 41));
            plot.setBackgroundPaint(Color.black);

            chart.setBackgroundPaint(medicalInfoPanelColor);

            ChartPanel chartPanel = new ChartPanel(chart);
            temperaturePanel.add(chartPanel, BorderLayout.CENTER);
        }

        temperaturePanel.revalidate();
        temperaturePanel.repaint();
    }

    private void updateHeartRateGraph() {
        heartRatePanel.removeAll();

        JSONArray heart_rates = new JSONArray(dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/get_heart_rate/" + horseID));

        //current time
        currentTimeMillis = System.currentTimeMillis();
        //earliest time in specified period
        earliestTimeMillis = currentTimeMillis - (hoursBack * 60L * 60L * 1000L);
        //time from latest datapoint
        try {
            latestDataTimeMillis = dateFormat.parse(heart_rates.getJSONObject(0).getString("ts")).getTime();
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }

        //If there is no data for the specified time period
        if( latestDataTimeMillis < earliestTimeMillis){
            JLabel noData = new JLabel("No data", SwingConstants.CENTER);
            noData.setFont(new Font("Arial", Font.BOLD, 30));
            heartRatePanel.add(noData);
        }else {
            TimeSeries series = new TimeSeries("Heart_rate");
            calculateAndAddToSeries(heart_rates, series, "heart_rate");

            TimeSeriesCollection dataset = new TimeSeriesCollection();
            dataset.addSeries(series);

            String title = "Heart rate of " + horse.getString("name") + " : " + getLatestValue(heart_rates, "heart_rate") +"bpm";
            JFreeChart chart = ChartFactory.createTimeSeriesChart(
                    title,          // Title
                    "",             // X-Axis label
                    "",             // Y-Axis label
                    dataset,        // Dataset
                    false,          // Legend
                    true,           // Tooltips
                    false           // URLs
            );

            XYPlot plot = chart.getXYPlot();
            plot.setBackgroundPaint(Color.black);
            plot.getRangeAxis().setRange(new Range(60, 100));

            chart.setBackgroundPaint(medicalInfoPanelColor);

            ChartPanel chartPanel = new ChartPanel(chart);
            heartRatePanel.add(chartPanel, BorderLayout.CENTER);
        }

        heartRatePanel.revalidate();
        heartRatePanel.repaint();
    }

    //Create a data series where data points are combined into specified intervals
    private void calculateAndAddToSeries(JSONArray values, TimeSeries series, String value) {
        int intervalMinutes = hoursBack*2;
        Map<Long, List<Integer>> groupedvalues = new TreeMap<>();

        // Iterate over the temperature readings
        for (int i = 0; i < values.length(); i++) {
            JSONObject tempObject = values.getJSONObject(i);
            try {
                Date date = dateFormat.parse(tempObject.getString("ts"));
                if (date.getTime() >= earliestTimeMillis) {  // Check if the timestamp is within the desired range
                    long timeInMinutes = date.getTime() / (1000 * 60); // Convert timestamp to minutes
                    long intervalKey = timeInMinutes / intervalMinutes; // Group by interval

                    // Initialize list if this is the first entry for this interval
                    groupedvalues.putIfAbsent(intervalKey, new ArrayList<>());
                    if(value.equals("temp")) {
                        groupedvalues.get(intervalKey).add(tempObject.getInt("temperature"));
                    }else{
                        groupedvalues.get(intervalKey).add(tempObject.getInt("heart_rate"));
                    }
                }
            } catch (ParseException e) {
                e.printStackTrace(); // Handle parse exceptions appropriately
            }
        }

        // Calculate the average for each interval and add to the series
        for (Map.Entry<Long, List<Integer>> entry : groupedvalues.entrySet()) {
            double average = entry.getValue().stream().mapToInt(Integer::intValue).average().orElse(Double.NaN);
            if (!Double.isNaN(average)) {
                Date averageDate = new Date(entry.getKey() * intervalMinutes * 60 * 1000);
                series.add(new Minute(averageDate), average);
            }
        }
    }

    //get the "current" temperature / heart rate
    //this is an average over the last (sampleLength) minutes
    private double getLatestValue(JSONArray values, String value) {
        Date lastTimeStamp;
        Date timeStamp;
        try {
            lastTimeStamp = dateFormat.parse(values.getJSONObject(0).getString("ts"));
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }

        //Get the average temperature of the last (sampleLength) minutes
        int sampleLength = 2;
        double sum = 0;
        double count = 0;
        for (int i = 0; i < values.length(); i++) {
            JSONObject tempObject = values.getJSONObject(i);

            try {
                timeStamp = dateFormat.parse(tempObject.getString("ts"));
            } catch (ParseException e) {
                throw new RuntimeException(e);
            }

            int diff = (int) (lastTimeStamp.getTime() - timeStamp.getTime());
            if (diff > 60000 * sampleLength) {
                count = i;
                break;
            }
            //if the difference is to large the temperature should not be added to the sum
            if(value.equals("temp")) {
                sum += tempObject.getInt("temperature");
            }else{
                sum += tempObject.getInt("heart_rate");
            }
        }
        double valueE0;
        valueE0 = sum / count;
        //Display 1 decimal
        int valueE1 = (int) Math.round(valueE0 * 10);

        return valueE1 / 10.0;
    }


    private static double calculate_azimuth_from_coordinates(double lat1, double lon1, double lat2, double lon2){
        double lat1_rad = Math.toRadians(lat1);
        double lon1_rad = Math.toRadians(lon1);
        double lat2_rad = Math.toRadians(lat2);
        double lon2_rad = Math.toRadians(lon2);

        double delta_lon = lon2_rad - lon1_rad;

        double y = Math.sin(delta_lon) * Math.cos(lat2_rad);
        double x = Math.cos(lat1_rad) * Math.sin(lat2_rad) - Math.sin(lat1_rad) * Math.cos(lat2_rad) * Math.cos(delta_lon);

        double azimuth_rad = Math.atan2(y, x);
        double azimuth_deg = Math.toDegrees(azimuth_rad);

        azimuth_deg = (azimuth_deg + 360) % 360;

        return azimuth_deg;
    }


    private void moveServoToHorse(){
        String response = dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/get_gps_camera/" + 1);
        JSONArray jsonArray = new JSONArray(response);
        JSONObject jsonObject = jsonArray.getJSONObject(0);
        double latitudeCamera = jsonObject.getDouble("latitude");
        double longitudeCamera = jsonObject.getDouble("longitude");
        double azimuth_origin = jsonObject.getDouble("azimuth");

        response = dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/get_gps_horse/" + horseID);
        jsonArray = new JSONArray(response);
        jsonObject = jsonArray.getJSONObject(0);
        double latitudeHorse = jsonObject.getDouble("latitude");
        double longitudeHorse = jsonObject.getDouble("longitude");

        if(latitudeHorse == 0 || longitudeHorse == 0){
            return;
        }


        double azimuth_calculated =  calculate_azimuth_from_coordinates(latitudeCamera, longitudeCamera, latitudeHorse, longitudeHorse);
        double azimuth_relative = (azimuth_calculated - azimuth_origin) % 360;

        if(azimuth_relative < 90 || azimuth_relative > 270){
            if(azimuth_relative > 270){
                azimuth_relative -= 360;
            }
        }else if(azimuth_relative > 180){
            azimuth_relative = -90;
        }else{
            azimuth_relative = 90;
        }

        int angle = (int) -Math.round(azimuth_relative);

        dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/update_servo_alpha/" + angle + "/1");
    }
}
