import java.io.*; // Got lazy and imported everything
import java.net.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
//Quintin d'Hotman de Villiers u21513768
// Create each question as a separate object
class Question {
    private String question;
    private List<String> answers;
    private List<String> correctAnswers;

    public Question(String question, List<String> answers, List<String> correctAnswers) {
        this.question = question;
        this.answers = answers;
        this.correctAnswers = correctAnswers;
    }

    public String getQuestion() {
        return question;
    }

    public List<String> getAnswers() {
        return answers;
    }

    public List<String> getCorrectAnswers() {
        return correctAnswers;
    }
}

public class TestServer {
    private static final int PORT = 55555; // Server port
    private static List<Question> questionList = new ArrayList<>(); // List of questions

    public static void main(String[] args) {
        loadQuestionsFromFile("questions.txt"); // Load questions and answers from file

        // Start the server
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("Test server is running and listening on port " + PORT);
            System.out.println("\u001B[32mHello! Welcome to the Test Server!\u001B[0m"); // Green color for hello
                                                                                         // message

            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("Connection received from " + clientSocket.getInetAddress());

                PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
                displayAsciiArt(out, clientSocket);
                // out.println("\u001B[32mHello! Welcome to the Test Server!\u001B[0m"); //
                // Green color for hello message
                // handleClient(clientSocket);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void loadQuestionsFromFile(String filename) {
        // Load questions and answers from file into questionList
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            String currentQuestion = null;
            List<String> currentAnswers = new ArrayList<>();
            List<String> currentCorrectAnswers = new ArrayList<>();
            while ((line = reader.readLine()) != null) {
                if (line.startsWith("?")) {
                    if (currentQuestion != null) {
                        questionList.add(new Question(currentQuestion, new ArrayList<>(currentAnswers),
                                new ArrayList<>(currentCorrectAnswers)));
                        currentAnswers.clear();
                        currentCorrectAnswers.clear();
                    }
                    currentQuestion = line.substring(1); // Remove leading "?" from question
                } else if (line.startsWith("+")) {
                    currentAnswers.add(line.substring(1)); // Remove leading "+" from answer
                    currentCorrectAnswers.add(line.substring(1));
                } else if (line.startsWith("-")) {
                    currentAnswers.add(line.substring(1)); // Remove leading "-" from wrong answer
                }
            }
            // Add last question
            if (currentQuestion != null) {
                questionList.add(new Question(currentQuestion, new ArrayList<>(currentAnswers),
                        new ArrayList<>(currentCorrectAnswers)));
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void handleClient(Socket clientSocket) {
        try (BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true)) {

            out.println(
                    "\u001B[32mPlease answer the following question by entering a letter corresponding to the correct answer!\u001B[0m"); // Green
                                                                                                                                          // color
                                                                                                                                          // for
                                                                                                                                          // hello
                                                                                                                                          // message
            Random random = new Random();
            int index = random.nextInt(questionList.size());
            Question selectedQuestion = questionList.get(index);

            String question = selectedQuestion.getQuestion();
            List<String> questionAnswers = selectedQuestion.getAnswers(); // Get answers for the selected question
            List<String> correctAnswers = selectedQuestion.getCorrectAnswers(); // Get correct answers for the selected
                                                                                // question

            if (questionAnswers.isEmpty() && correctAnswers.isEmpty()) {
                out.println("Invalid question. Please try again.");
                handleClient(clientSocket); // Recursive call to handle another question
                return;
            }

            if (correctAnswers.isEmpty() || correctAnswers.size() < 1) {
                String tempAnswer = "None of the above";
                correctAnswers.clear();
                correctAnswers.add(tempAnswer);
                if (!questionAnswers.contains(tempAnswer)) {
                    questionAnswers.add(tempAnswer);
                }
            } else if (correctAnswers.size() > 1) {
                String tempAnswer = "Some of the above";
                correctAnswers.clear();
                correctAnswers.add(tempAnswer);
                if (!questionAnswers.contains(tempAnswer)) {
                    questionAnswers.add(tempAnswer);
                }
            }

            // Display question
            int questionLength = question.length();
            int padding = (80 - questionLength) / 2; // Center horizontally
            String paddingStr = String.format("%" + padding + "s", "");

            out.println(paddingStr + "\u001B[36m" + question + "\u001B[0m"); // Cyan color for question
            for (int i = 0; i < questionAnswers.size(); i++) {
                out.println(paddingStr + (char) ('a' + i) + ") " + questionAnswers.get(i)); // Display answers with
                                                                                            // letters
            }

            out.println(
                    "\u001B[36mPlease enter the letter corresponding to your answer (e.g., a, b, c, d, ...):\u001B[0m");
            // Read user's answer
            String userAnswer = in.readLine().trim();
            int userChoiceIndex = userAnswer.toUpperCase().charAt(0) - 'A'; // Convert letter to index (0-based)

            // Check if answer is correct
            if (userChoiceIndex >= 0 && userChoiceIndex < questionAnswers.size()) {
                String userChoice = questionAnswers.get(userChoiceIndex);
                if (correctAnswers.contains(userChoice)) {
                    out.println("\u001B[32mCongratulations! Your answer is correct.\u001B[0m");
                } else {
                    out.println("\u001B[31mIncorrect answer. The correct answer(s) is/are: "
                            + String.join(", ", correctAnswers) + "\u001B[0m"); // Red color for incorrect answer
                }
            } else {
                out.println(
                        "\u001B[31mInvalid choice. Please enter a letter corresponding to one of the answers.\u001B[0m");
            }

            // Ask if the user wants to continue
            out.println("Do you want to answer another question? (yes/no)");
            String continueAnswer = in.readLine().trim().toLowerCase();
            if (continueAnswer.equals("no")) {
                out.println("Thank you for playing.");
                clientSocket.close();
            } else {
                handleClient(clientSocket); // Recursive call to handle another question
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void displayAsciiArt(PrintWriter out, Socket clientSocket) {
          String[] asciiArtLines = {

              " __    __     _                            _ ",
              "/ / /\\ \\___| | ___ ___  _ __ ___   ___  / \\",
              "\\ \\/  \\/ / _ \\ |/ __/ _ \\| '_ ` _ \\ / _ \\/  /",
              " \\  /\\  /  __/ | (_| (_) | | | | | |  __/\\_/ ",
              "  \\/  \\/ \\___|_|\\___\\___/|_| |_| |_|\\___\\/   ",
              "                                             ",
                

          };

          // Send each line of ASCII art with a delay
          Timer timer = new Timer();
          int delay = 500; // Delay between each line (milliseconds)
        AtomicInteger index = new AtomicInteger(0);

        TimerTask task = new TimerTask() {
            @Override
            public void run() {
                if (index.get() < asciiArtLines.length) {
                    out.println(asciiArtLines[index.getAndIncrement()]);
                } else {
                    timer.cancel(); // Stop the timer when all lines are sent
                    handleClient(clientSocket);
                }
            }
        };

        timer.schedule(task, 0, delay);
    }
}
