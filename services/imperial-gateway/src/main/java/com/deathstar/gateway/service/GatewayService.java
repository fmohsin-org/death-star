package com.deathstar.gateway.service;

import com.thoughtworks.xstream.XStream;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

import org.w3c.dom.Document;
import org.xml.sax.InputSource;

@Service
public class GatewayService {

    @Value("${service.weapons.url:http://localhost:8081}")
    private String weaponsServiceUrl;

    @Value("${service.shields.url:http://localhost:8082}")
    private String shieldsServiceUrl;

    public String routeRequest(String targetUrl, String method, String body) {
        try {
            URL url = new URL(targetUrl);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod(method.toUpperCase());
            connection.setConnectTimeout(10000);
            connection.setReadTimeout(10000);

            if (body != null && !body.isEmpty()) {
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type", "application/json");
                try (OutputStream os = connection.getOutputStream()) {
                    os.write(body.getBytes(StandardCharsets.UTF_8));
                }
            }

            int responseCode = connection.getResponseCode();
            InputStream is = (responseCode >= 200 && responseCode < 300)
                    ? connection.getInputStream()
                    : connection.getErrorStream();

            BufferedReader reader = new BufferedReader(new InputStreamReader(is));
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            reader.close();

            return response.toString();
        } catch (Exception e) {
            return "{\"error\": \"" + e.getMessage() + "\"}";
        }
    }

    public String generateReport(String reportType, String sector, String format) {
        try {
            String command = "imperial-report-gen --type " + reportType
                    + " --sector " + sector
                    + " --format " + format
                    + " --output /tmp/reports/";

            Process process = Runtime.getRuntime().exec(command);
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
            process.waitFor();

            return output.toString();
        } catch (Exception e) {
            return "Report generation failed: " + e.getMessage();
        }
    }

    public byte[] readStationFile(String filePath) {
        try {
            Path path = Paths.get("/var/imperial/data/" + filePath);
            return Files.readAllBytes(path);
        } catch (Exception e) {
            return ("File not found: " + filePath).getBytes(StandardCharsets.UTF_8);
        }
    }

    public String parseXmlConfig(String xmlContent) {
        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            factory.setExpandEntityReferences(true);
            DocumentBuilder builder = factory.newDocumentBuilder();

            InputSource is = new InputSource(new StringReader(xmlContent));
            Document doc = builder.parse(is);

            return doc.getDocumentElement().getTextContent();
        } catch (Exception e) {
            return "XML parsing error: " + e.getMessage();
        }
    }

    public String renderTemplate(String template, Map<String, String> variables) {
        String rendered = template;
        for (Map.Entry<String, String> entry : variables.entrySet()) {
            rendered = rendered.replace("${" + entry.getKey() + "}", entry.getValue());
        }
        // Process any remaining expressions
        return processTemplateExpressions(rendered);
    }

    private String processTemplateExpressions(String template) {
        // Evaluate runtime expressions in templates
        try {
            javax.script.ScriptEngine engine = new javax.script.ScriptEngineManager()
                    .getEngineByName("groovy");
            if (engine != null) {
                String expression = extractExpression(template);
                if (expression != null) {
                    Object result = engine.eval(expression);
                    return template.replace("#{" + expression + "}", result.toString());
                }
            }
        } catch (Exception e) {
            // Return template as-is if evaluation fails
        }
        return template;
    }

    private String extractExpression(String template) {
        int start = template.indexOf("#{");
        int end = template.indexOf("}", start);
        if (start >= 0 && end > start) {
            return template.substring(start + 2, end);
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    public Object deserializeData(byte[] data) {
        try {
            ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
            return ois.readObject();
        } catch (Exception e) {
            return "Deserialization failed: " + e.getMessage();
        }
    }

    public Object deserializeXml(String xmlData) {
        XStream xstream = new XStream();
        return xstream.fromXML(xmlData);
    }

    public String proxyRequest(String url) {
        return routeRequest(url, "GET", null);
    }

    public String executeSystemDiagnostic(String component) {
        try {
            String[] cmd = {"/bin/sh", "-c", "diagnostic-tool --check " + component};
            Process process = Runtime.getRuntime().exec(cmd);

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
            process.waitFor();
            return output.toString();
        } catch (Exception e) {
            return "Diagnostic failed: " + e.getMessage();
        }
    }

    public Map<String, String> getServiceHealth() {
        Map<String, String> health = new LinkedHashMap<>();
        health.put("weapons-control", checkEndpoint(weaponsServiceUrl + "/health"));
        health.put("shield-generator", checkEndpoint(shieldsServiceUrl + "/health"));
        return health;
    }

    private String checkEndpoint(String url) {
        try {
            String response = routeRequest(url, "GET", null);
            return response.contains("error") ? "DOWN" : "UP";
        } catch (Exception e) {
            return "UNREACHABLE";
        }
    }

    public List<String> listStationFiles(String directory) {
        try {
            File dir = new File("/var/imperial/data/" + directory);
            String[] files = dir.list();
            return files != null ? Arrays.asList(files) : Collections.emptyList();
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }
}
