package com.library;

import java.time.LocalDate;
import java.util.List;
import java.util.Scanner;

/** Console menu for the library system. */
public class Main {
    public static void main(String[] args) {
        Database db = new Database();
        try {
            db.init();
        } catch (Exception e) {
            System.out.println("Could not connect to the database: " + e.getMessage());
            System.out.println("Check library.db.url / user / password (see README).");
            return;
        }
        LibraryService svc = new LibraryService(db);
        Scanner in = new Scanner(System.in);
        while (true) {
            System.out.println("\n=== Library Management System ===");
            System.out.println("1. Add book   2. Add member   3. Search books");
            System.out.println("4. Issue book 5. Return book  6. Active loans   0. Exit");
            System.out.print("Choose: ");
            String choice = in.nextLine().trim();
            try {
                switch (choice) {
                    case "1" -> {
                        System.out.print("Title: "); String t = in.nextLine();
                        System.out.print("Author: "); String a = in.nextLine();
                        System.out.print("Copies: "); int n = Integer.parseInt(in.nextLine().trim());
                        System.out.println("Book added with id " + svc.addBook(t, a, n));
                    }
                    case "2" -> {
                        System.out.print("Name: "); String n = in.nextLine();
                        System.out.print("Email: "); String e = in.nextLine();
                        System.out.println("Member added with id " + svc.addMember(n, e));
                    }
                    case "3" -> {
                        System.out.print("Keyword: ");
                        List<LibraryService.Book> r = svc.searchBooks(in.nextLine());
                        if (r.isEmpty()) System.out.println("No books found.");
                        r.forEach(b -> System.out.printf("[%d] %s by %s (%d/%d available)%n",
                                b.id(), b.title(), b.author(), b.available(), b.total()));
                    }
                    case "4" -> {
                        System.out.print("Book id: "); int b = Integer.parseInt(in.nextLine().trim());
                        System.out.print("Member id: "); int m = Integer.parseInt(in.nextLine().trim());
                        int id = svc.issueBook(b, m, LocalDate.now());
                        System.out.println("Issued. Issue id " + id + ", due in " + LibraryService.LOAN_DAYS + " days.");
                    }
                    case "5" -> {
                        System.out.print("Issue id: "); int id = Integer.parseInt(in.nextLine().trim());
                        int fine = svc.returnBook(id, LocalDate.now());
                        System.out.println(fine == 0 ? "Returned on time. No fine." : "Returned late. Fine: Rs. " + fine);
                    }
                    case "6" -> {
                        List<LibraryService.Loan> loans = svc.activeLoans();
                        if (loans.isEmpty()) System.out.println("No active loans.");
                        loans.forEach(l -> System.out.printf("Issue %d: '%s' -> %s (due %s)%n",
                                l.id(), l.bookTitle(), l.memberName(), l.due()));
                    }
                    case "0" -> { System.out.println("Goodbye."); return; }
                    default -> System.out.println("Invalid choice.");
                }
            } catch (NumberFormatException e) {
                System.out.println("Please enter a valid number.");
            } catch (LibraryException e) {
                System.out.println("Error: " + e.getMessage());
            } catch (Exception e) {
                System.out.println("Database error: " + e.getMessage());
            }
        }
    }
}
