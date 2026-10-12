# Library Management System (Java, JDBC, MySQL)

**Stack:** Java 17+, OOP, JDBC, MySQL

Console application to manage books, members, issuing, returns and late fines.

## Features
- Add books and members (validation, duplicate email check)
- Search books by title or author
- Issue a book (14-day loan, max 3 active loans per member)
- Return a book with automatic fine (Rs. 2 per late day)
- List active loans
- Issue and return run inside **JDBC transactions** (commit/rollback) so stock and loan records stay consistent
- All queries use `PreparedStatement` (no SQL injection)

## Run with MySQL
1. Install MySQL and run `mysql -u root -p < schema.sql`
2. Download the MySQL Connector/J jar (mysql-connector-j) into `lib/`
3. Compile and run:
```bash
mkdir -p out && javac -d out src/com/library/*.java
java -Dlibrary.db.url=jdbc:mysql://localhost:3306/librarydb \
     -Dlibrary.db.user=root -Dlibrary.db.password=YOUR_PASSWORD \
     -cp "out:lib/*" com.library.Main
```
(On Windows use `;` instead of `:` in the classpath.)

## Run the tests (no MySQL needed)
The tests use a temporary SQLite database. Put an `sqlite-jdbc` jar (3.42.x) in `lib/`, then:
```bash
javac -d out src/com/library/*.java
java -cp "out:lib/*" com.library.LibraryServiceTest
```
13 checks cover search, stock changes, fines, double returns and loan limits.

## Structure
`Database` (connections, schema) - `LibraryService` (business logic) - `LibraryException` (rule violations) - `Main` (menu) - `LibraryServiceTest`.
