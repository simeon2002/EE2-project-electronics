import javax.swing.*;
import java.awt.*;
import java.util.Objects;

public class SplashScreen extends JFrame {
    public SplashScreen() {
        Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
        setTitle("Horse Management System");

        double size = 0;
        if (screenSize.getHeight() > screenSize.getWidth()) {
            size = (screenSize.getWidth() / 2);
        } else {
            size = (screenSize.getHeight() / 2);
        }

        setSize((int) size, (int) size); // Chose size
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        ImageIcon imageIcon = new ImageIcon(Objects.requireNonNull(getClass().getResource("/resources/splash_image.png")));
        Image image = imageIcon.getImage();
        Image newImgage = image.getScaledInstance((int) size - 20, (int) size - 40, Image.SCALE_SMOOTH);
        imageIcon = new ImageIcon(newImgage);

        JLabel label = new JLabel(imageIcon);
        getContentPane().add(label);
        setLocationRelativeTo(null);
        setVisible(true);

        new Thread(() -> {
            try {
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            SwingUtilities.invokeLater(() -> {
                new HorseManagement();
                dispose();
            });
        }).start();
    }
}
