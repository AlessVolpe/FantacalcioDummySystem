package dataHandling;

import java.io.IOException;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;

import java.net.Socket;

import java.util.ArrayList;
import java.util.Hashtable;
import java.util.regex.Pattern;

import javax.naming.NamingEnumeration;
import javax.naming.NamingException;
import javax.naming.directory.Attribute;
import javax.naming.directory.Attributes;
import javax.naming.directory.DirContext;

public class EmailValidator {
    public static boolean emailPatternMatches(String emailAddress) {
        String regexPattern = "^(?=.{1,64}@)[A-Za-z0-9_-]+(\\.[A-Za-z0-9_-]+)*@"
                + "[^-][A-Za-z0-9-]+(\\.[A-Za-z0-9-]+)*(\\.[A-Za-z]{2,})$";

        return Pattern
                .compile(regexPattern)
                .matcher(emailAddress)
                .matches();
    }

    public static boolean emailDNSLookup(String emailAddress) {
        int position = emailAddress.indexOf('@');
        if (position == -1) return false;
        String hostName = emailAddress.substring(++position);

        ArrayList<String> mxList;
        try {
            mxList = DNSLookup.lookupMX(hostName);
        } catch (NamingException e) {
            System.err.println(e.getMessage());
            return false;
        }

        if (mxList.isEmpty()) return false;
        for (String s : mxList) {
            boolean valid = false;

            try {
                int res;
                Socket socket = new Socket(s, 25);
                BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));

                res = DNSLookup.hear(reader);
                if (res != 220) {
                    reader.close();
                    writer.close();
                    socket.close();
                    throw new Exception("Invalid header");
                }
                DNSLookup.say(writer, "EHLO " + hostName);

                res = DNSLookup.hear(reader);
                if (res != 250) {
                    reader.close();
                    writer.close();
                    socket.close();
                    throw new Exception("Not ESMTP");
                }
                DNSLookup.say(writer, "MAIL FROM: <admin@" + hostName + ">");

                res = DNSLookup.hear(reader);
                if (res != 250) {
                    reader.close();
                    writer.close();
                    socket.close();
                    throw new Exception("Sender rejected");
                }

                DNSLookup.say(writer, "RCPT TO: <" + emailAddress + ">");

                res = DNSLookup.hear(reader);
                DNSLookup.say(writer, "RSET");
                DNSLookup.hear(reader);
                DNSLookup.say(writer, "QUIT");
                DNSLookup.hear(reader);
                if (res != 250) {
                    reader.close();
                    writer.close();
                    socket.close();
                    throw new Exception("Address is not valid!");
                }

                valid = true;
                reader.close();
                writer.close();
                socket.close();
            } catch (Exception ignored) {
            }
            if (valid) return true;
        }
        return false;
    }

    static class DNSLookup {
        static int hear(BufferedReader reader) throws IOException {
            String line;
            int res = 0;

            while ((line = reader.readLine()) != null) {
                String prefix = line.substring(0, 3);
                try {
                    res = Integer.parseInt(prefix);
                } catch (Exception e) {
                    res = -1;
                }
                if (line.charAt(3) != '-')
                    break;
            }
            return res;
        }

        static void say(BufferedWriter writer, String text) throws IOException {
            writer.write(text + "\r\n");
            writer.flush();
        }

        static ArrayList<String> lookupMX(String hostName) throws NamingException {
            Hashtable<String, String> env = new Hashtable<>();
            env.put("java.naming.factory.initial", "com.sun.jndi.dns.DnsContextFactory");

            DirContext ictx = new javax.naming.directory.InitialDirContext(env);
            Attributes attrs = ictx.getAttributes(hostName, new String[] { "MX" });
            Attribute attr = attrs.get("MX");

            if ((attr == null) || (attr.size() == 0)) {
                attrs = ictx.getAttributes(hostName, new String[] { "A" });
                attr = attrs.get("A");
                if (attr == null)
                    throw new NamingException("No match for name '" + hostName + "'");
            }

            ArrayList<String> res = new ArrayList<>();
            NamingEnumeration<?> en = attr.getAll();
            while (en.hasMore()) {
                String x = (String) en.next();
                String[] f = x.split(" ");
                if (f[1].endsWith("."))
                    f[1] = f[1].substring(0, (f[1].length() - 1));
                res.add(f[1]);
            }
            return res;
        }
    }
}
