import org.json.JSONArray;
import org.json.JSONObject;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;


public class HorseManagement extends JFrame {

    private static JLabel cameraView;

    JScrollPane scrollPane;
    JPanel horseButtonPanel;
    JPanel alarmPanel;
    JPanel buttonPanel;
    JPanel sidePanel;
    JPanel mainPanel;
    JPanel cameraPanel;

    ArrayList<JButton> horseButtons;

    Camera camera;
    DBR dbr;
    JSONArray horses;

    boolean toggle;

    int numberOfHorses;
    int sidePanelWidth = 300;

    Color sidePanelColor;

    Timer timer1;
    Timer timer2;

    public HorseManagement() {
        setTitle("Horse Management System");
        Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
        //setSize((int) screenSize.getWidth(), (int) screenSize.getHeight());
        setExtendedState(JFrame.MAXIMIZED_BOTH);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        dbr = new DBR();
        cameraView = new JLabel();
        camera = Camera.getInstance();

        sidePanelColor = Color.lightGray;

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

        //Every minute: scrollbar
        timer2 = new Timer(60000, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                try {
                    updateGUI(3);
                } catch (Exception ex) {
                    ex.printStackTrace();
                }
            }
        });
        timer2.start();
    }

    public void initGUI(){
        setLayout(new BorderLayout());
        camera.setCameraView(cameraView);

        alarmPanel = new JPanel(new GridLayout(0, 1));
        horseButtonPanel = new JPanel(new GridLayout(0, 1));
        mainPanel = new JPanel(new BorderLayout());
        cameraPanel = new JPanel(new BorderLayout());
        cameraPanel.setBackground(Color.BLACK);
        scrollPane = new JScrollPane(horseButtonPanel);
        scrollPane.setPreferredSize(new Dimension(200, Integer.MAX_VALUE));


        initSidePanel();

        cameraPanel.add(cameraView, BorderLayout.CENTER);
        cameraPanel.add(sidePanel, BorderLayout.EAST);

        mainPanel.add(cameraPanel, BorderLayout.CENTER);

        add(scrollPane, BorderLayout.WEST);
        add(mainPanel, BorderLayout.CENTER);
    }

    private void initButtons(){
        // Create buttons
        JButton upButton = new JButton("Up");
        JButton leftButton = new JButton("Left");
        JButton rightButton = new JButton("Right");
        JButton downButton = new JButton("Down");

        upButton.setFont(new Font("Arial", Font.BOLD, 20));
        leftButton.setFont(new Font("Arial", Font.BOLD, 20));
        rightButton.setFont(new Font("Arial", Font.BOLD, 20));
        downButton.setFont(new Font("Arial", Font.BOLD, 20));

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

        initButtons();

        alarmPanel.setBackground(sidePanelColor);
        buttonPanel.setBackground(sidePanelColor);
        sidePanel.setBackground(sidePanelColor);

        sidePanel.add(alarmPanel);
        sidePanel.add(new JLabel(""));
        sidePanel.add(buttonPanel);
    }


    private void updateGUI(int n) {
        updateHorses();

        switch (n) {
            case 1:
                updateAlarms();
                break;
            case 3:
                updateScrollPanel();
                break;
            default:
                updateAlarms();
                updateScrollPanel();
                break;
        }
    }

    private void updateHorses(){
        horses = new JSONArray(dbr.makeGETRequest("https://studev.groept.be/api/a23ib2d03/get_horses"));
        numberOfHorses = horses.length();
    }

    private void updateScrollPanel(){
        updateHorses();

        horseButtons = new ArrayList<>();
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
            horseButtons.add(horseButtonTemp);
        }


        horseButtonPanel.removeAll();
        for (JButton button : horseButtons) {
            button.setBorder(BorderFactory.createCompoundBorder(button.getBorder(), BorderFactory.createEmptyBorder(5, 0, 5, 0)));
            horseButtonPanel.add(button);
        }

        horseButtonPanel.revalidate();
        horseButtonPanel.repaint();
    }

    private void updateAlarms(){
        alarmPanel.removeAll();

        toggle = !toggle;

        for (int i = 0; i < numberOfHorses; i++) {
            JSONObject horse = horses.getJSONObject(i);

            int alarm = horse.getInt("alarm");
            String name = horse.getString("name");
            int id = horse.getInt("horseID");

            if(alarm == 1){

                JButton alarmButton = new JButton(name);
                if(toggle) {
                    alarmButton.setBackground(Color.yellow);
                }else{
                    alarmButton.setBackground(Color.red);
                }
                alarmButton.setFont(new Font("Arial", Font.BOLD, 30));
                alarmButton.addActionListener(e -> {
                    SwingUtilities.invokeLater(() -> new HorseManagementHorsePage(id));
                    timer1.stop();
                    timer2.stop();
                    this.dispose();
                });
                alarmPanel.add(alarmButton);
            }
        }

        alarmPanel.revalidate();
        alarmPanel.repaint();
    }
}