package com.mycompany.app;

import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;

/**
 * Java Web Application with Built-in HTTP Server
 */
public class WebApp {

    private static final String MESSAGE = "Hello World from VibeCoding Java App!";
    private static final int PORT = getPort();

    private static int getPort() {
        String port = System.getenv("PORT");
        return port != null ? Integer.parseInt(port) : 8080;
    }

    public static void main(String[] args) throws IOException {
        // Create HTTP server
        HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);
        
        // Create handlers
        server.createContext("/", new RootHandler());
        server.createContext("/health", new HealthHandler());
        server.createContext("/api/message", new MessageHandler());
        
        // Start server
        server.setExecutor(null);
        server.start();
        
        System.out.println("Java HTTP Server started on port " + PORT);
        System.out.println("Access the application at: http://localhost:" + PORT);
    }

    // Root handler
    static class RootHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String response = "<!DOCTYPE html>\n" +
                "<html>\n" +
                "<head>\n" +
                "    <title>VibeCoding Java App</title>\n" +
                "    <style>\n" +
                "        body { font-family: Arial, sans-serif; margin: 40px; }\n" +
                "        .container { max-width: 600px; margin: 0 auto; text-align: center; }\n" +
                "        .message { color: #007acc; font-size: 24px; margin: 20px 0; }\n" +
                "        .info { color: #666; margin: 10px 0; }\n" +
                "    </style>\n" +
                "</head>\n" +
                "<body>\n" +
                "    <div class=\"container\">\n" +
                "        <h1>🚀 VibeCoding Java Application</h1>\n" +
                "        <div class=\"message\">" + MESSAGE + "</div>\n" +
                "        <div class=\"info\">\n" +
                "            <p><strong>Java Version:</strong> " + System.getProperty("java.version") + "</p>\n" +
                "            <p><strong>Web Server:</strong> Java SE Embedded HTTP Server</p>\n" +
                "            <p><strong>Runtime:</strong> " + System.getProperty("java.runtime.name") + "</p>\n" +
                "        </div>\n" +
                "        <div>\n" +
                "            <a href=\"/api/message\">API Endpoint</a> | \n" +
                "            <a href=\"/health\">Health Check</a>\n" +
                "        </div>\n" +
                "    </div>\n" +
                "</body>\n" +
                "</html>";
            
            exchange.getResponseHeaders().set("Content-Type", "text/html; charset=UTF-8");
            exchange.sendResponseHeaders(200, response.getBytes().length);
            OutputStream os = exchange.getResponseBody();
            os.write(response.getBytes());
            os.close();
        }
    }

    // Health check handler
    static class HealthHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String response = "{\n" +
                "    \"status\": \"UP\",\n" +
                "    \"timestamp\": " + System.currentTimeMillis() + ",\n" +
                "    \"java\": {\n" +
                "        \"version\": \"" + System.getProperty("java.version") + "\",\n" +
                "        \"runtime\": \"" + System.getProperty("java.runtime.name") + "\",\n" +
                "        \"webServer\": \"Java SE Embedded HTTP Server\"\n" +
                "    },\n" +
                "    \"application\": {\n" +
                "        \"name\": \"VibeCoding Java App\",\n" +
                "        \"version\": \"1.0-SNAPSHOT\"\n" +
                "    }\n" +
                "}";
            
            exchange.getResponseHeaders().set("Content-Type", "application/json");
            exchange.sendResponseHeaders(200, response.getBytes().length);
            OutputStream os = exchange.getResponseBody();
            os.write(response.getBytes());
            os.close();
        }
    }

    // Message API handler
    static class MessageHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String response = "{\n" +
                "    \"message\": \"" + MESSAGE + "\",\n" +
                "    \"timestamp\": " + System.currentTimeMillis() + ",\n" +
                "    \"server\": \"Java SE Embedded HTTP Server\",\n" +
                "    \"version\": \"Built-in with Java " + System.getProperty("java.version") + "\"\n" +
                "}";
            
            exchange.getResponseHeaders().set("Content-Type", "application/json");
            exchange.sendResponseHeaders(200, response.getBytes().length);
            OutputStream os = exchange.getResponseBody();
            os.write(response.getBytes());
            os.close();
        }
    }
}
