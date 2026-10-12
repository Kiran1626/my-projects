package com.library;

import java.sql.*;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;

/** All library operations, using JDBC prepared statements. */
public class LibraryService {
    public static final int LOAN_DAYS = 14;
    public static final int FINE_PER_DAY = 2;      // Rs. per late day
    public static final int MAX_ACTIVE_LOANS = 3;  // per member

    public record Book(int id, String title, String author, int available, int total) {}
    public record Loan(int id, String bookTitle, String memberName, LocalDate issued, LocalDate due) {}

    private final Database db;
    public LibraryService(Database db) { this.db = db; }

    public int addBook(String title, String author, int copies) throws SQLException, LibraryException {
        if (title == null || title.isBlank() || author == null || author.isBlank() || copies < 1)
            throw new LibraryException("Title, author and at least 1 copy are required.");
        String sql = "INSERT INTO books (title, author, total_copies, available_copies) VALUES (?,?,?,?)";
        try (Connection c = db.connect(); PreparedStatement ps = c.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            ps.setString(1, title.trim()); ps.setString(2, author.trim()); ps.setInt(3, copies); ps.setInt(4, copies);
            ps.executeUpdate();
            try (ResultSet k = ps.getGeneratedKeys()) { k.next(); return k.getInt(1); }
        }
    }

    public int addMember(String name, String email) throws SQLException, LibraryException {
        if (name == null || name.isBlank() || email == null || !email.contains("@"))
            throw new LibraryException("A name and valid email are required.");
        try (Connection c = db.connect(); PreparedStatement ps = c.prepareStatement(
                "INSERT INTO members (name, email) VALUES (?,?)", Statement.RETURN_GENERATED_KEYS)) {
            ps.setString(1, name.trim()); ps.setString(2, email.trim().toLowerCase());
            ps.executeUpdate();
            try (ResultSet k = ps.getGeneratedKeys()) { k.next(); return k.getInt(1); }
        } catch (SQLException e) {
            if (String.valueOf(e.getMessage()).toLowerCase().contains("unique") || e.getErrorCode() == 1062)
                throw new LibraryException("A member with this email already exists.");
            throw e;
        }
    }

    public List<Book> searchBooks(String keyword) throws SQLException {
        String sql = "SELECT id, title, author, available_copies, total_copies FROM books "
                   + "WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ? ORDER BY title";
        String like = "%" + keyword.toLowerCase() + "%";
        List<Book> out = new ArrayList<>();
        try (Connection c = db.connect(); PreparedStatement ps = c.prepareStatement(sql)) {
            ps.setString(1, like); ps.setString(2, like);
            try (ResultSet r = ps.executeQuery()) {
                while (r.next()) out.add(new Book(r.getInt(1), r.getString(2), r.getString(3), r.getInt(4), r.getInt(5)));
            }
        }
        return out;
    }

    /** Issues a book inside a transaction so stock and loan record stay consistent. */
    public int issueBook(int bookId, int memberId, LocalDate issueDate) throws SQLException, LibraryException {
        try (Connection c = db.connect()) {
            c.setAutoCommit(false);
            try {
                if (!exists(c, "SELECT 1 FROM members WHERE id = ?", memberId)) throw new LibraryException("Member not found.");
                int available;
                try (PreparedStatement ps = c.prepareStatement("SELECT available_copies FROM books WHERE id = ?")) {
                    ps.setInt(1, bookId);
                    try (ResultSet r = ps.executeQuery()) {
                        if (!r.next()) throw new LibraryException("Book not found.");
                        available = r.getInt(1);
                    }
                }
                if (available < 1) throw new LibraryException("No copies of this book are available.");
                try (PreparedStatement ps = c.prepareStatement(
                        "SELECT COUNT(*) FROM issues WHERE member_id = ? AND return_date IS NULL")) {
                    ps.setInt(1, memberId);
                    try (ResultSet r = ps.executeQuery()) {
                        r.next();
                        if (r.getInt(1) >= MAX_ACTIVE_LOANS)
                            throw new LibraryException("Member already has " + MAX_ACTIVE_LOANS + " books issued.");
                    }
                }
                int issueId;
                try (PreparedStatement ps = c.prepareStatement(
                        "INSERT INTO issues (book_id, member_id, issue_date, due_date) VALUES (?,?,?,?)",
                        Statement.RETURN_GENERATED_KEYS)) {
                    ps.setInt(1, bookId); ps.setInt(2, memberId);
                    ps.setString(3, issueDate.toString()); ps.setString(4, issueDate.plusDays(LOAN_DAYS).toString());
                    ps.executeUpdate();
                    try (ResultSet k = ps.getGeneratedKeys()) { k.next(); issueId = k.getInt(1); }
                }
                try (PreparedStatement ps = c.prepareStatement(
                        "UPDATE books SET available_copies = available_copies - 1 WHERE id = ?")) {
                    ps.setInt(1, bookId); ps.executeUpdate();
                }
                c.commit();
                return issueId;
            } catch (SQLException | LibraryException e) {
                c.rollback();
                throw e;
            }
        }
    }

    /** Returns a book and gives back the fine in Rs. (0 if on time). */
    public int returnBook(int issueId, LocalDate returnDate) throws SQLException, LibraryException {
        try (Connection c = db.connect()) {
            c.setAutoCommit(false);
            try {
                int bookId; LocalDate due;
                try (PreparedStatement ps = c.prepareStatement(
                        "SELECT book_id, due_date, return_date FROM issues WHERE id = ?")) {
                    ps.setInt(1, issueId);
                    try (ResultSet r = ps.executeQuery()) {
                        if (!r.next()) throw new LibraryException("Issue record not found.");
                        if (r.getString(3) != null) throw new LibraryException("This book was already returned.");
                        bookId = r.getInt(1); due = LocalDate.parse(r.getString(2));
                    }
                }
                long lateDays = Math.max(0, ChronoUnit.DAYS.between(due, returnDate));
                int fine = (int) (lateDays * FINE_PER_DAY);
                try (PreparedStatement ps = c.prepareStatement("UPDATE issues SET return_date = ?, fine = ? WHERE id = ?")) {
                    ps.setString(1, returnDate.toString()); ps.setInt(2, fine); ps.setInt(3, issueId); ps.executeUpdate();
                }
                try (PreparedStatement ps = c.prepareStatement(
                        "UPDATE books SET available_copies = available_copies + 1 WHERE id = ?")) {
                    ps.setInt(1, bookId); ps.executeUpdate();
                }
                c.commit();
                return fine;
            } catch (SQLException | LibraryException e) {
                c.rollback();
                throw e;
            }
        }
    }

    public List<Loan> activeLoans() throws SQLException {
        String sql = "SELECT i.id, b.title, m.name, i.issue_date, i.due_date FROM issues i "
                   + "JOIN books b ON b.id = i.book_id JOIN members m ON m.id = i.member_id "
                   + "WHERE i.return_date IS NULL ORDER BY i.due_date";
        List<Loan> out = new ArrayList<>();
        try (Connection c = db.connect(); Statement s = c.createStatement(); ResultSet r = s.executeQuery(sql)) {
            while (r.next()) out.add(new Loan(r.getInt(1), r.getString(2), r.getString(3),
                    LocalDate.parse(r.getString(4)), LocalDate.parse(r.getString(5))));
        }
        return out;
    }

    private boolean exists(Connection c, String sql, int id) throws SQLException {
        try (PreparedStatement ps = c.prepareStatement(sql)) {
            ps.setInt(1, id);
            try (ResultSet r = ps.executeQuery()) { return r.next(); }
        }
    }
}
