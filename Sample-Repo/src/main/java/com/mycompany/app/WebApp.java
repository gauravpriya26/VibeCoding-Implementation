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
    private static final int PORT = 8080;

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
            String response = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>VibeCoding Java App</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; }
                        .container { max-width: 600px; margin: 0 auto; text-align: center; }
                        .message { color: #007acc; font-size: 24px; margin: 20px 0; }
                        .info { color: #666; margin: 10px 0; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🚀 VibeCoding Java Application</h1>
                        <div class="message">""" + MESSAGE + """
                        </div>
                        <div class="info">
                            <p><strong>Java Version:</strong> """ + System.getProperty("java.version") + """
                            </p>
                            <p><strong>Web Server:</strong> Java SE Embedded HTTP Server</p>
                            <p><strong>Runtime:</strong> """ + System.getProperty("java.runtime.name") + """
                            </p>
                        </div>
                        <div>
                            <a href="/api/message">API Endpoint</a> | 
                            <a href="/health">Health Check</a>
                        </div>
                    </div>
                </body>
                </html>
                """;
            
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
            String response = """
                {
                    "status": "UP",
                    "timestamp": """ + System.currentTimeMillis() + """,
                    "java": {
                        "version": """ + "\"" + System.getProperty("java.version") + "\"" + """,
                        "runtime": """ + "\"" + System.getProperty("java.runtime.name") + "\"" + """,
                        "webServer": "Java SE Embedded HTTP Server"
                    },
                    "application": {
                        "name": "VibeCoding Java App",
                        "version": "1.0-SNAPSHOT"
                    }
                }
                """;
            
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
            String response = """
                {
                    "message": """ + "\"" + MESSAGE + "\"" + """,
                    "timestamp": """ + System.currentTimeMillis() + """,
                    "server": "Java SE Embedded HTTP Server",
                    "version": "Built-in with Java """ + System.getProperty("java.version") + """
                }
                """;
            
            exchange.getResponseHeaders().set("Content-Type", "application/json");
            exchange.sendResponseHeaders(200, response.getBytes().length);
            OutputStream os = exchange.getResponseBody();
            os.write(response.getBytes());
            os.close();
        }
    }
}
