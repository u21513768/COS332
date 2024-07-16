import java.io.*; //Quintin d'Hotman de Villiers u21513768
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

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
    private static final int PORT = 8080; // Server port
    private static List<Question> questionList = new ArrayList<>(); // List of questions
    private static String serverInfo = System.getProperty("java.vm.name") + " " + System.getProperty("java.vm.version");

    public static void main(String[] args) {
        loadQuestionsFromFile("questions.txt"); // Load questions and answers from file
        InetAddress ip;
        String hostname;
        // Start the server
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("Server information: " + serverInfo);

            ip = InetAddress.getLocalHost();
            hostname = ip.getHostName();

            System.out.println("Your current IP address : " + ip);
            System.out.println("Your current Hostname : " + hostname);
            System.out.println("Test server is running and listening on port " + PORT);
            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("Connection received from " + clientSocket.getInetAddress());

                handleClient(clientSocket, ip, hostname);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        // } catch (UnknownHostException e) {
        // e.printStackTrace();
        // }
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

                if (currentCorrectAnswers.size() < 1) {
                    // If there is only one correct answer, add it to the answers list
                    // System.out.println("None of the above");
                    currentAnswers.add("None of the above/below");
                    currentCorrectAnswers.add("None of the above/below");
                }

                if (currentCorrectAnswers.size() > 1 && currentCorrectAnswers.contains("None of the above/below")) {
                    // If there are multiple correct answers, add them to the answers list
                    currentAnswers.remove("None of the above/below");
                    currentCorrectAnswers.remove("None of the above/below");
                    // System.out.println("Removal of None of the above");
                } else if (currentCorrectAnswers.size() > 1
                        && !currentCorrectAnswers.contains("None of the above/below")) {
                    // If there are multiple correct answers, add them to the answers list
                    if (currentAnswers.contains("Some of the above/below")) {
                        currentCorrectAnswers.clear();
                        currentCorrectAnswers.add("Some of the above/below");
                    } else {
                        currentAnswers.add("Some of the above/below");
                        currentCorrectAnswers.clear();
                        currentCorrectAnswers.add("Some of the above/below");
                        // System.out.println("Some of the above");
                    }
                }
            }

            // Add last question
            if (currentQuestion != null) {
                questionList.add(new Question(currentQuestion, new ArrayList<>(currentAnswers),
                        new ArrayList<>(currentCorrectAnswers)));
            }

            // Logging questions, answers, and correct answers for debugging
            // for (Question q: questionList) {
            // System.out.println(q.getQuestion());
            // System.out.println(q.getAnswers());
            // System.out.println(q.getCorrectAnswers());
            // }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void handleClient(Socket clientSocket, InetAddress ip, String hostname) {
        try (BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true)) {
    
            Question selectedQuestion = getCurrentQuestion();
    
            String question = selectedQuestion.getQuestion();
            List<String> questionAnswers = selectedQuestion.getAnswers();
            List<String> correctAnswers = selectedQuestion.getCorrectAnswers();
    
            String request = in.readLine();
            System.out.println(request);
    
            if (request == null) {
                // Bad request - No request received
                sendErrorResponse(out, 400, "Bad Request", "No request received.");
                clientSocket.close();
                return;
            }
    
            if (request.contains("goodbye")) {
                // Send HTTP response for goodbye page
                sendGoodbyePage(out);
                clientSocket.close();
                return;
            } else if (request.contains("do-not-click")) {
                // Send HTTP response for "DO NOT CLICK" page
                sendDoNotClickPage(out);
            } else if (request != null && request.contains("POST")) {
                System.out.println("Email button clicked");
                StringBuilder requestBody = new StringBuilder();
                while (in.ready()) {
                    requestBody.append((char) in.read());
                }
                // System.out.println(requestBody);
                String body = requestBody.toString();
                body = body.substring(body.indexOf("question"));
                System.out.println(body);
                String[] parts = body.split("&");
                String mySelectedQuestion = "";
                String mySelectedAnswer = "";
                String myAnswer = "";
                for (String part : parts) {
                    // System.out.println(part);
                    String[] pair = part.split("=", 2); // Limiting split to 2 parts to handle "=" in answer
                    if (pair.length == 2) {
                        String key = URLDecoder.decode(pair[0], StandardCharsets.UTF_8);
                        String value = URLDecoder.decode(pair[1], StandardCharsets.UTF_8);
                        if (key.equals("question")) {
                            mySelectedQuestion = value;
                        } else if (key.equals("selectedAnswer")) {
                            mySelectedAnswer = value;
                        } else if (key.equals("answers")) {
                            myAnswer = value;
                        }
                    }
                }
                // Now mySelectedQuestion contains the question string and mySelectedAnswer
                // contains the answer string
                sendQuestionByEmailAsync(mySelectedQuestion, mySelectedAnswer, myAnswer);
                System.out.println("After email");
                sendQuestionPage(out, question, questionAnswers, correctAnswers);
            } else {
                // Send HTTP response headers for question page
                sendQuestionPage(out, question, questionAnswers, correctAnswers);
            }
            
            clientSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    private static void sendGoodbyePage(PrintWriter out) {
        String imagePath = "./network2.jpg";
        String imageBase64 = getImageAsBase64(imagePath);
        // Send HTTP response headers for goodbye page
        out.println("HTTP/1.1 200 OK");
        out.println("Date: " + new Date()); // Include Date field
        out.println("Server: " + serverInfo); // Include Server field
        out.println("Content-Type: text/html");
        // out.println("Content-Length: 100"); // Include Content-Length field
        out.println();
        // Send HTML content for goodbye page
        out.println("<!DOCTYPE html>");
        out.println("<html>");
        out.println("<head>");
        out.println("<title>Goodbye</title>");
        out.println("<meta charset='UTF-8'>");
        out.println("<meta name='viewport' content='width=device-width, initial-scale=1.0'>");
        // Include Bootstrap CSS
        out.println(
                "<link href='https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css' rel='stylesheet'>");
        out.println("<style>");
        out.println("body {");
        out.println("    background-image: url('data:image/jpeg;base64," + imageBase64 + "');");
        out.println("    background-size: cover;");
        out.println("}");
        out.println(".question-container {");
        out.println("    background-color: rgba(255, 255, 255, 0.9);");
        out.println("    padding: 20px;");
        out.println("    border-radius: 10px;");
        out.println("}");
        out.println("</style>");
        out.println("</head>");
        out.println("<body class='p-5 m-5'>");
        out.println("<div class='container question-container'>");
        out.println("<h1>Goodbye!</h1>");
        out.println("<p>Thank you for playing the quiz.</p>");
        out.println("</div");
        out.println("</body>");
        out.println("</html>");
    }

    private static void sendQuestionPage(PrintWriter out, String question, List<String> questionAnswers,
            List<String> correctAnswers) {

        // Load the image file
        String imagePath = "./network.jpg";
        String imageBase64 = getImageAsBase64(imagePath);
        // Send HTTP response headers for question page
        out.println("HTTP/1.1 200 OK");
        out.println("Date: " + new Date()); // Include Date field
        out.println("Server: " + serverInfo); // Include Server field
        out.println("Content-Type: text/html");
        // out.println("Content-Length: 100"); // Include Content-Length field
        out.println();
        // Send HTML content for question page
        out.println("<!DOCTYPE html>");
        out.println("<html>");
        out.println("<head>");
        out.println("<title>Test Server</title>");
        out.println("<meta charset='UTF-8'>");
        out.println("<meta name='viewport' content='width=device-width, initial-scale=1.0'>");
        // Include Bootstrap CSS
        out.println(
                "<link href='https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css' rel='stylesheet'>");
        out.println("<style>");
        out.println("body {");
        out.println("    background-image: url('data:image/jpeg;base64," + imageBase64 + "');");
        out.println("    background-size: cover;");
        out.println("}");
        out.println(".position-bottom-right {");
        out.println("    position: fixed;");
        out.println("    bottom: 20px;");
        out.println("    right: 20px;");
        out.println("}");
        out.println(".question-container {");
        out.println("    background-color: rgba(255, 255, 255, 0.9);");
        out.println("    padding: 20px;");
        out.println("    border-radius: 10px;");
        out.println("}");
        out.println("</style>");
        out.println("<script>");
        out.println("function checkAnswer() {");
        out.println("  var selectedAnswer = document.querySelector('input[name=answer]:checked');");
        out.println("  var selectedQuestion = '" + question + "';"); // Include selected question
        out.println("  var correctAnswers = [" + "\"" + String.join("\", \"", correctAnswers) + "\"" + "];");
        out.println("  var feedback = document.getElementById('feedback');");
        out.println("  var source = document.getElementById('footer');");
        out.println("  var nextQuestionButton = document.getElementById('nextQuestionButton');");
        out.println("  var emailButton = document.getElementById('emailButton');");
        out.println("  var quitButton = document.getElementById('quitButton');");
        out.println("  if (selectedAnswer) {");
        out.println("    if (correctAnswers.includes(selectedAnswer.value)) {");
        out.println("      feedback.innerHTML = 'Congratulations! Your answer is correct.';");
        out.println("      feedback.style.color = 'green';");
        out.println("    } else {");
        out.println("      feedback.innerHTML = 'Incorrect answer. The correct answer(s) is/are: "
                + String.join(", ", correctAnswers) + "';");
        out.println("      feedback.style.color = 'red';");
        out.println("    }");
        out.println("    source.innerHTML = 'Some network guy probably ';");
        out.println("    source.style.display = 'block';");
        out.println("    nextQuestionButton.style.display = 'inline-block';");
        out.println("    emailButton.style.display = 'inline-block';");
        out.println("    quitButton.style.display = 'inline-block';");
        out.println("  } else {");
        out.println("    feedback.innerHTML = 'Please select an answer.';");
        out.println("    feedback.style.color = 'black';");
        out.println("  }");
        out.println("}");
        out.println("function showEmailSentAlert() {");
        out.println("  alert('Email sent successfully');");
        out.println("}");
        out.println("</script>");
        out.println("</head>");

        out.println("<body class='p-5 m-5'>");
        out.println("<div class='container question-container'>");
        out.println("<h1>Quiz</h1>");
        out.println("<h3>" + question + "</h3>");
        out.println("<p>Please select the correct answer.</p>");
        out.println("<div class='row'>");
        out.println("<div class='col-5'>");
        out.println("<form method=\"post\" onsubmit=\"checkAnswer(); return false;\">");
        for (int i = 0; i < questionAnswers.size(); i++) {
            out.println("<div class='form-check'>");
            out.println("<input class='form-check-input' type=\"radio\" name=\"answer\" value=\""
                    + questionAnswers.get(i) + "\">" + questionAnswers.get(i) + "<br/>");
            out.println("</div>");
        }
        out.println("<input type=\"submit\" value=\"Submit\" class='btn btn-primary m-1 mt-3'>");
        out.println("</form>");
        out.println("</div>");
        out.println("<div class='col-5'>");
        out.println("<blockquote id='blockQuote' class='blockquote text-center'>");
        out.println("<p id=\"feedback\" class='lead'></p>");
        out.println("<footer class='blockquote-footer' id='footer' style=\"display:none;\"></footer>");

        out.println("</blockquote>");
        out.println("</div>");
        out.println("</div>");
        // Button Group
        out.println("<div class='button-group'>");
        out.println(
                "<button id=\"nextQuestionButton\" style=\"display:none;\" onclick=\"location.reload();\" class='button-group-button btn btn-warning m-1'>Answer Another Question</button>");
        out.println(
                "<button id=\"emailButton\" style=\"display:none;\" class='button-group-button btn btn-success m-1'>Email Answers</button>");
        out.println(
                "<button id=\"quitButton\" onclick=\"window.location.href='/goodbye';\" class='button-group-button btn btn-danger m-1'>Quit</button>");

        out.println("</div>");
        out.println("</div>");

        out.println("<script>");
        out.println("document.getElementById('emailButton').addEventListener('click', function() {");
        out.println("    showEmailSentAlert();");
        out.println("    var form = document.createElement('form');");
        out.println("    form.method = 'POST';");
        out.println("    form.action = '/';");
        out.println("    var inputQuestion = document.createElement('input');");
        out.println("    inputQuestion.type = 'hidden';");
        out.println("    inputQuestion.name = 'question';");
        out.println("    inputQuestion.value = '" + question + "';");
        out.println("    form.appendChild(inputQuestion);");
        out.println("    var inputSelectedAnswer = document.createElement('input');");
        out.println("    inputSelectedAnswer.type = 'hidden';");
        out.println("    inputSelectedAnswer.name = 'selectedAnswer';");
        out.println("    var selectedAnswer = document.querySelector('input[name=answer]:checked').value;");
        out.println("    inputSelectedAnswer.value = selectedAnswer;");
        out.println("    form.appendChild(inputSelectedAnswer);");
        out.println("    var inputAnswers = document.createElement('input');");
        out.println("    inputAnswers.type = 'hidden';");
        out.println("    inputAnswers.name = 'answers';");
        out.println("    var answersArray = [" + "\"" + String.join("\", \"", correctAnswers) + "\"" + "];"); // Populate with correct answers
        out.println("    inputAnswers.value = answersArray.join(',');");
        out.println("    form.appendChild(inputAnswers);");
        out.println("    document.body.appendChild(form);");
        out.println("    form.submit();");
        out.println("});");
        out.println("</script>");
        
        
        // DO NOT CLICK BUTTON
        out.println(
                "<button onclick=\"window.location.href='/do-not-click';\" class='btn btn-outline-danger m-1 position-bottom-right'>DO NOT CLICK</button>");
        out.println("</body>");
        out.println("</html>");
    }

    private static String getImageAsBase64(String imagePath) {
        try {
            InputStream inputStream = new FileInputStream(imagePath);
            byte[] bytes = new byte[inputStream.available()];
            inputStream.read(bytes);
            inputStream.close();
            return Base64.getEncoder().encodeToString(bytes);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return "";
    }

    private static void sendDoNotClickPage(PrintWriter out) {
        // Send HTTP response headers for the "DO NOT CLICK" page
        out.println("HTTP/1.1 200 OK");
        out.println("Date: " + new Date()); // Include Date field
        out.println("Server: " + serverInfo); // Include Server field
        out.println("Content-Type: text/html");
        // out.println("Content-Length: 100"); // Include Content-Length field
        out.println();
        // Send HTML content for the "DO NOT CLICK" page
        out.println("<!DOCTYPE html>");
        out.println("<html>");
        out.println("<head>");
        out.println("<meta charset='UTF-8'>");
        out.println("<meta name='viewport' content='width=device-width, initial-scale=1.0'>");
        out.println("<title>DO NOT CLICK</title>");
        out.println("<style>");
        out.println("html, body {");
        out.println("    margin: 0;");
        out.println("    padding: 0;");
        out.println("    width: 100%;");
        out.println("    height: 100%;");
        out.println("    overflow: hidden;");
        out.println("    position: relative;"); // Ensure relative positioning for absolute div
        out.println("}");
        out.println("#message-overlay {");
        out.println("    position: absolute;");
        out.println("    top: 50%;");
        out.println("    left: 50%;");
        out.println("    transform: translate(-50%, -50%);");
        out.println("    background-color: rgba(0, 0, 0, 0.5);");
        out.println("    color: white;");
        out.println("    padding: 30px;");
        out.println("    border-radius: 10px;");
        out.println("}");
        out.println("iframe {");
        out.println("    width: 100%;");
        out.println("    height: 100%;");
        out.println("    border: none;");
        out.println("}");
        out.println("</style>");
        out.println("</head>");
        out.println("<body>");
        out.println(
                "<iframe src='https://www.youtube.com/embed/wKbU8B-QVZk?autoplay=1' frameborder='0'allow='autoplay; encrypted-media' allowfullscreen></iframe>");
        out.println("<div id='message-overlay'>");
        out.println("    <h1>I will never financially recover</h1>");
        out.println("</div>");
        out.println("</body>");
        out.println("</html>");
    }

    private static void sendErrorResponse(PrintWriter out, int statusCode, String statusMessage, String errorMessage) {
        // Send HTTP response headers for error
        out.println("HTTP/1.1 " + statusCode + " " + statusMessage);
        out.println("Date: " + new Date()); // Include Date field
        out.println("Server: " + serverInfo); // Include Server field
        out.println("Content-Type: text/html");
        // out.println("Content-Length: 100"); // Include Content-Length field
        out.println();
        // Send HTML content for error
        out.println("<!DOCTYPE html>");
        out.println("<html>");
        out.println("<head>");
        out.println("<title>Error</title>");
        out.println("</head>");
        out.println("<body>");
        out.println("<h1>Error " + statusCode + ": " + statusMessage + "</h1>");
        out.println("<p>" + errorMessage + "</p>");
        out.println("</body>");
        out.println("</html>");
    }

    private static Question getCurrentQuestion() {
        Random random = new Random();
        int index = random.nextInt(questionList.size());
        return questionList.get(index);
    }

    private static void sendQuestionByEmail(String question, String userAnswer, String correctAnswers) {
        try {
            System.out.println("Sending email...");
            // Define Postfix server details
            String serverHost = "localhost"; // Assuming the Postfix server is running on the same machine
            int serverPort = 25;
            String senderEmail = "test@milk.com"; // Update with a valid sender email address within your domain
            String recipientEmail = "quintin@milk.com"; // Update with a valid recipient email address within your
                                                        // domain
            String senderDomain = "milk.com";
    
            // Prepare email content
            String subject = "Quiz Question";
            String body = "Question:\n " + question + "\n\n";
            body += "Your Answer:\n " + userAnswer + "\n\n";
            body += "Correct Answer(s):\n";
            body += correctAnswers + "\n";
    
            // Establish connection to SMTP server
            Socket socket = new Socket(serverHost, serverPort);
            BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
    
            // Send email
            writer.write("HELO " + senderDomain + "\r\n");
            writer.write("MAIL FROM: <" + senderEmail + ">\r\n");
            writer.write("RCPT TO: <" + recipientEmail + ">\r\n");
            writer.write("DATA\r\n");
            writer.write("Subject: " + subject + "\r\n");
            writer.write("\r\n");
            writer.write(body + "\r\n.\r\n");
            writer.flush();
    
            // Read response from server
            String response;
            while ((response = reader.readLine()) != null) {
                System.out.println(response);
            }
    
            // Close connection
            writer.write("QUIT\r\n");
            writer.flush();
            writer.close();
            reader.close();
            socket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }   
    
    private static void sendQuestionByEmailAsync(String question, String userAnswer, String correctAnswers) {
        new Thread(() -> sendQuestionByEmail(question, userAnswer, correctAnswers)).start();
    }
}
