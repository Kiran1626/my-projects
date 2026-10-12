package com.library;

/** Business-rule violation (e.g. no copies left, member not found). */
public class LibraryException extends Exception {
    public LibraryException(String message) { super(message); }
}
