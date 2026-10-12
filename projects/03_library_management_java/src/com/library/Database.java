package com.library;

import java.sql.*;

/** Creates JDBC connections and the tables. Defaults to MySQL; override with system properties. */
public class Database {
    private final String url;
    private final String user;
    private final String password;

    public Database() {
        this(System.getProperty("library.db.url", "jdbc:mysql://localhost:3306/librarydb"),
             System.getProperty("library.db.user", "root"),
             System.getProperty("library.db.password", ""));
    }

    public Database(String url, String user, String password) {
        this.url = url; this.user = user; this.password = password;
    }

    public Connection connect() throws SQLException {
        return DriverManager.getConnection(url, user, password);
    }

    /** Creates tables if they do not exist. MySQL is the target; SQLite is supported for testing. */
    public void init() throws SQLException {
        boolean sqlite = url.startsWith("jdbc:sqlite");
        String pk = sqlite ? "INTEGER PRIMARY KEY AUTOINCREMENT" : "INT AUTO_INCREMENT PRIMARY KEY";
        try (Connection c = connect(); Statement s = c.createStatement()) {
            s.execute("CREATE TABLE IF NOT EXISTS books (id " + pk + ", title VARCHAR(200) NOT NULL, "
                    + "author VARCHAR(120) NOT NULL, total_copies INT NOT NULL, available_copies INT NOT NULL)");
            s.execute("CREATE TABLE IF NOT EXISTS members (id " + pk + ", name VARCHAR(100) NOT NULL, "
                    + "email VARCHAR(120) NOT NULL UNIQUE)");
            s.execute("CREATE TABLE IF NOT EXISTS issues (id " + pk + ", book_id INT NOT NULL, member_id INT NOT NULL, "
                    + "issue_date VARCHAR(10) NOT NULL, due_date VARCHAR(10) NOT NULL, return_date VARCHAR(10), "
                    + "fine INT NOT NULL DEFAULT 0, FOREIGN KEY (book_id) REFERENCES books(id), "
                    + "FOREIGN KEY (member_id) REFERENCES members(id))");
        }
    }
}
