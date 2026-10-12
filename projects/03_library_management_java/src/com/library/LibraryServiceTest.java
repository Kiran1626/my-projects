package com.library;

import java.io.File;
import java.time.LocalDate;

/** Plain-Java tests (no framework needed). Run: see README. Uses a temporary SQLite file. */
public class LibraryServiceTest {
    static int passed = 0;

    static void check(boolean cond, String name) {
        if (!cond) throw new AssertionError("FAILED: " + name);
        passed++; System.out.println("PASS  " + name);
    }

    static void expectError(Runnable2 r, String name) {
        try { r.run(); } catch (LibraryException e) { passed++; System.out.println("PASS  " + name + " -> " + e.getMessage()); return; }
        catch (Exception e) { throw new AssertionError("Wrong exception in " + name + ": " + e); }
        throw new AssertionError("FAILED (no error): " + name);
    }

    interface Runnable2 { void run() throws Exception; }

    public static void main(String[] args) throws Exception {
        File f = File.createTempFile("library-test", ".db");
        f.deleteOnExit();
        Database db = new Database("jdbc:sqlite:" + f.getAbsolutePath(), "", "");
        db.init();
        LibraryService svc = new LibraryService(db);

        int b1 = svc.addBook("Clean Code", "Robert Martin", 2);
        int b2 = svc.addBook("Operating Systems", "Galvin", 1);
        int m1 = svc.addMember("Asha", "asha@example.com");
        int m2 = svc.addMember("Ravi", "ravi@example.com");
        check(svc.searchBooks("clean").size() == 1, "search by title keyword");
        check(svc.searchBooks("galvin").get(0).title().equals("Operating Systems"), "search by author");

        LocalDate day0 = LocalDate.of(2026, 1, 1);
        int issue1 = svc.issueBook(b1, m1, day0);
        check(svc.searchBooks("clean").get(0).available() == 1, "stock decreases on issue");
        check(svc.activeLoans().size() == 1, "active loan listed");

        int issue2 = svc.issueBook(b2, m2, day0);
        expectError(() -> svc.issueBook(b2, m1, day0), "cannot issue when no copies left");
        expectError(() -> svc.addMember("Asha2", "asha@example.com"), "duplicate email rejected");
        expectError(() -> svc.issueBook(999, m1, day0), "unknown book rejected");
        expectError(() -> svc.issueBook(b1, 999, day0), "unknown member rejected");

        check(svc.returnBook(issue2, day0.plusDays(10)) == 0, "no fine when returned on time");
        check(svc.returnBook(issue1, day0.plusDays(20)) == 6 * LibraryService.FINE_PER_DAY, "fine for 6 late days = Rs. 12");
        expectError(() -> svc.returnBook(issue1, day0.plusDays(21)), "double return rejected");
        check(svc.searchBooks("clean").get(0).available() == 2, "stock restored on return");

        int b3 = svc.addBook("DBMS", "Korth", 5);
        for (int i = 0; i < 3; i++) svc.issueBook(b3, m1, day0);
        expectError(() -> svc.issueBook(b3, m1, day0), "max 3 active loans per member");

        System.out.println("\nAll " + passed + " checks passed.");
    }
}
