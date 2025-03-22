import streamlit as st  # type: ignore
import sqlite3
import os

# Database setup
def init_db():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            year INTEGER,
            isbn TEXT
        )
    """)
    conn.commit()
    return conn

# Add a book
def add_book(conn):
    st.subheader("Add a New Book")
    title = st.text_input("Title")
    author = st.text_input("Author")
    genre = st.text_input("Genre")
    year = st.number_input("Publication Year", min_value=0, max_value=2100, step=1)
    isbn = st.text_input("ISBN")
    if st.button("Add Book"):
        if title and author:  # Basic validation
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO books (title, author, genre, year, isbn)
                VALUES (?, ?, ?, ?, ?)
            """, (title, author, genre, year, isbn))
            conn.commit()
            st.success("Book added successfully!")
        else:
            st.error("Title and Author are required fields.")

# View all books
def view_books(conn):
    st.subheader("Your Library")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    if books:
        # Adding column headers for better readability
        st.table({"ID": [b[0] for b in books], 
                  "Title": [b[1] for b in books], 
                  "Author": [b[2] for b in books], 
                  "Genre": [b[3] for b in books], 
                  "Year": [b[4] for b in books], 
                  "ISBN": [b[5] for b in books]})
    else:
        st.write("No books in the library yet.")

# Search for a book
def search_books(conn):
    st.subheader("Search for a Book")
    search_term = st.text_input("Enter search term (title/author/genre):").lower()
    if search_term:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM books
            WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR LOWER(genre) LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        results = cursor.fetchall()
        if results:
            st.table({"ID": [r[0] for r in results], 
                      "Title": [r[1] for r in results], 
                      "Author": [r[2] for r in results], 
                      "Genre": [r[3] for r in results], 
                      "Year": [r[4] for r in results], 
                      "ISBN": [r[5] for r in results]})
        else:
            st.write("No books found.")

# Update book details
def update_book(conn):
    st.subheader("Update Book Details")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM books")
    books = cursor.fetchall()
    if books:
        book_options = {f"{book[1]} (ID: {book[0]})": book[0] for book in books}
        selected_book = st.selectbox("Select a book to update", list(book_options.keys()))
        book_id = book_options[selected_book]
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        if book:
            title = st.text_input("Title", book[1])
            author = st.text_input("Author", book[2])
            genre = st.text_input("Genre", book[3])
            year = st.number_input("Publication Year", value=book[4], min_value=0, max_value=2100, step=1)
            isbn = st.text_input("ISBN", book[5])
            if st.button("Update Book"):
                cursor.execute("""
                    UPDATE books
                    SET title = ?, author = ?, genre = ?, year = ?, isbn = ?
                    WHERE id = ?
                """, (title, author, genre, year, isbn, book_id))
                conn.commit()
                st.success("Book updated successfully!")
    else:
        st.write("No books in the library yet.")

# Delete a book
def delete_book(conn):
    st.subheader("Delete a Book")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM books")
    books = cursor.fetchall()
    if books:
        book_options = {f"{book[1]} (ID: {book[0]})": book[0] for book in books}
        selected_book = st.selectbox("Select a book to delete", list(book_options.keys()))
        book_id = book_options[selected_book]
        if st.button("Delete Book"):
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()
            st.success("Book deleted successfully!")
    else:
        st.write("No books in the library yet.")

# Home page
def home_page():
    st.title("📚 Welcome to Your Personal Library Manager")
    image_path = "library-image.jpg"
    if os.path.exists(image_path):
        st.image(image_path, caption="Your Personal Library", use_container_width=True)
    else:
        st.error(f"Image file '{image_path}' not found in {os.getcwd()}. Please ensure it’s in the same directory as this script.")
    st.write("""
        Use the sidebar to navigate through the app and manage your library.
        - **Add Book**: Add a new book to your library.
        - **View Books**: See all the books in your library.
        - **Search Books**: Search for a book by title, author, or genre.
        - **Update Book**: Edit the details of an existing book.
        - **Delete Book**: Remove a book from your library.
    """)

# Main app
def main():
    conn = init_db()

    # Sidebar for navigation
    st.sidebar.title("Menu")
    menu = st.sidebar.radio("Choose an option", ["Home", "Add Book", "View Books", "Search Books", "Update Book", "Delete Book"])

    if menu == "Home":
        home_page()
    elif menu == "Add Book":
        add_book(conn)
    elif menu == "View Books":
        view_books(conn)
    elif menu == "Search Books":
        search_books(conn)
    elif menu == "Update Book":
        update_book(conn)
    elif menu == "Delete Book":
        delete_book(conn)

    conn.close()  # Close the database connection when done

if __name__ == "__main__":
    main()
