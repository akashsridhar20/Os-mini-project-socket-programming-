"""
This is the server-side file for the Online Library Management System (OLMS).

For students, the following functionalities are provided:
    1. Authenticate student by username and password.
    2. Search for and borrow books.
    3. View the list of borrowed books.

For admins, the following functionalities are provided:
    1. Authenticate admin using a password.
    2. Modify book records: add, delete, or search for books.
    3. Access student information and manage new student records.

The server communicates with multiple clients using socket programming, ensuring concurrent access to the library database stored in CSV format. Data consistency is maintained through file-locking mechanisms.
"""

import socket
import threading
import csv
from datetime import datetime

# Define a lock for file access
file_lock = threading.Lock()

# Server configuration
SERVER_HOST = socket.gethostname()  # Get the hostname dynamically
SERVER_PORT = 5050
BUFFER_SIZE = 2048
ADMIN_PASS = "ad123"

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((SERVER_HOST, SERVER_PORT))
        server.listen()
        print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

        while True:
            client_socket, client_address = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()

def authenticate(client_socket):
    authentication_data = client_socket.recv(BUFFER_SIZE).decode().strip()
    if "@" not in authentication_data:
        return False, None  # Invalid authentication data format

    username, password = authentication_data.split("@")
    with open('students.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if str(row['username']) == username and str(row['password']) == password:
                return True, username

    return False, None

def borrowedBooks(client_socket, userid):
    book_id = None
    with open('students.csv', 'r') as students_file:
        students_reader = csv.DictReader(students_file)
        for row in students_reader:
            if row['username'] == userid:
                book_id = row['books_borrowed']
                break

    if book_id is None or book_id == '0':
        client_socket.sendall("No books borrowed.".encode())
        return

    borrowed_book_details = ""
    with open('books.csv', 'r') as books_file:
        books_reader = csv.DictReader(books_file)
        for book in books_reader:
            if book['book_id'] == book_id:
                borrowed_book_details = f"Book ID: {book['book_id']}, Title: {book['title']}, Author: {book['author']}, Genre: {book['genre']}, Year: {book['year']}"
                break

    client_socket.sendall(borrowed_book_details.encode())

def borrowBook(client_socket, user_id, book_id):
    book_found = False
    book_available = False
    book_title = ""

    with open('books.csv', 'r') as books_file:
        books_reader = csv.DictReader(books_file)
        books = list(books_reader)
        for book in books:
            if book['book_id'] == book_id:
                book_found = True
                if book['availability'] == 'Yes':
                    book_available = True
                    book_title = book['title']
                break

    if not book_found:
        client_socket.sendall("Book not found.".encode())
        return

    if not book_available:
        client_socket.sendall("Book is not available.".encode())
        return

    students_updated = []
    student_found = False

    with open('students.csv', 'r') as students_file:
        students_reader = csv.DictReader(students_file)
        for row in students_reader:
            if row['username'] == user_id:
                student_found = True
                if row['books_borrowed'] == '0':
                    row['books_borrowed'] = book_id
                else:
                    client_socket.sendall("You have already borrowed a book.".encode())
                    return
            students_updated.append(row)

    if not student_found:
        client_socket.sendall("User not found.".encode())
        return

    with open('students.csv', 'w', newline='') as students_file:
        fieldnames = ['username', 'password', 'student_name', 'rollno', 'phone_no', 'email_id', 'books_borrowed']
        writer = csv.DictWriter(students_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(students_updated)

    books_updated = []
    for book in books:
        if book['book_id'] == book_id:
            book['availability'] = 'No'
        books_updated.append(book)

    with open('books.csv', 'w', newline='') as books_file:
        fieldnames = ['book_id', 'title', 'author', 'genre', 'year', 'availability']
        writer = csv.DictWriter(books_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books_updated)

    client_socket.sendall(f"Book '{book_title}' successfully borrowed.".encode())

def searchBook(client_socket, search_parameter):
    results = []
    with open('books.csv', 'r') as books_file:
        books_reader = csv.DictReader(books_file)
        for book in books_reader:
            if (search_parameter.lower() in book['book_id'].lower() or
                search_parameter.lower() in book['title'].lower() or
                search_parameter.lower() in book['author'].lower() or
                search_parameter.lower() in book['genre'].lower()):
                book_details = f"Book ID: {book['book_id']}, Title: {book['title']}, Author: {book['author']}, Genre: {book['genre']}, Year: {book['year']}, Availability: {book['availability']}"
                results.append(book_details)

    if results:
        result_message = "\n".join(results)
    else:
        result_message = "No books found matching the search criteria."

    client_socket.sendall(result_message.encode())

def viewStudentDetails(client_socket, userid):
    student_details = ""
    with open('students.csv', 'r') as students_file:
        students_reader = csv.DictReader(students_file)
        for row in students_reader:
            if row['username'] == userid:
                student_details = f"Student ID: {row['username']}, Name: {row['student_name']}, Roll No: {row['rollno']}, Phone No: {row['phone_no']}, Email: {row['email_id']}, Books Borrowed: {row['books_borrowed']}"
                break

    if student_details:
        client_socket.sendall(student_details.encode())
    else:
        client_socket.sendall("Student details not found.".encode())

def modifyBook(client_socket, book_details):
    book_id, field, new_value = book_details.split("@")
    
    books_updated = []
    book_found = False

    with open('books.csv', 'r') as books_file:
        books_reader = csv.DictReader(books_file)
        for book in books_reader:
            if book['book_id'] == book_id:
                book_found = True
                if field in book:
                    book[field] = new_value
                else:
                    client_socket.sendall("Invalid field.".encode())
                    return
            books_updated.append(book)
    
    if not book_found:
        client_socket.sendall("Book ID not found.".encode())
        return

    with open('books.csv', 'w', newline='') as books_file:
        fieldnames = ['book_id', 'title', 'author', 'genre', 'year', 'availability']
        writer = csv.DictWriter(books_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books_updated)

    client_socket.sendall("Book details updated successfully.".encode())

def menuHandler(client_socket):
    while True:
        request = client_socket.recv(BUFFER_SIZE).decode().split("@")
        
        if request[0] == "borrowedbooks":
            borrowedBooks(client_socket, request[1])
        elif request[0] == "borrowbook":
            borrowBook(client_socket, request[1], request[2])
        elif request[0] == "searchbook":
            searchBook(client_socket, request[1])
        elif request[0] == "viewstudentdetails":
            viewStudentDetails(client_socket, request[1])
        elif request[0] == "admin":
            isAdmin(client_socket, request[1])
        elif request[0] == "modifybook":
            modifyBook(client_socket, "@".join(request[1:]))
        elif request[0] == "addbook":
            add_book(client_socket, "@".join(request[1:]))
        elif request[0] == "deletebook":
            deleteBook(client_socket, request[1])  # Pass the book ID for deletion
        else:
            client_socket.sendall("Invalid command.".encode())

def add_book(client_socket, book_details):
    try:
        # Split the book details
        book_id, title, author, genre, year, availability = book_details.split("@")

        # Read the current books from the CSV file
        books = read_csv('books.csv')

        # Check if the book ID already exists
        for book in books:
            if book['book_id'] == book_id:
                client_socket.sendall("Book ID already exists.".encode())
                return

        # Add the new book to the list
        new_book = {
            'book_id': book_id,
            'title': title,
            'author': author,
            'genre': genre,
            'year': year,
            'availability': availability
        }
        books.append(new_book)

        # Write the updated book list back to the CSV file
        write_csv('books.csv', books, ['book_id', 'title', 'author', 'genre', 'year', 'availability'])

        client_socket.sendall("Book added successfully.".encode())
    except Exception as e:
        logging.error(f"Error adding book: {e}")
        client_socket.sendall("Error adding book.".encode())

# Function to read CSV file while acquiring lock
def read_csv(file_name):
    try:
        with file_lock:
            with open(file_name, 'r') as file:
                return list(csv.DictReader(file))
    except Exception as e:
        logging.error(f"Error reading {file_name}: {e}")
        return []

# Function to write to CSV file while acquiring lock
def write_csv(file_name, data, fieldnames):
    try:
        with file_lock:
            with open(file_name, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
    except Exception as e:
        logging.error(f"Error writing to {file_name}: {e}")

def deleteBook(client_socket, book_id):
    try:
        # Read the current books from the CSV file
        books_updated = []
        book_found = False

        with open('books.csv', 'r') as books_file:
            books_reader = csv.DictReader(books_file)
            for book in books_reader:
                if book['book_id'] == book_id:
                    book_found = True
                else:
                    books_updated.append(book)

        if not book_found:
            client_socket.sendall("Book ID not found.".encode())
            return

        # Write the updated book list back to the CSV file
        with open('books.csv', 'w', newline='') as books_file:
            fieldnames = ['book_id', 'title', 'author', 'genre', 'year', 'availability']
            writer = csv.DictWriter(books_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(books_updated)

        client_socket.sendall("Book deleted successfully.".encode())
    except Exception as e:
        print(f"Error deleting book: {e}")
        client_socket.sendall("Error deleting book.".encode())

def isAdmin(client_socket, admin_pass):
    # print(admin_pass)
    if admin_pass == ADMIN_PASS:
        # print("true")
        client_socket.sendall("True".encode())
    else:
        # print("false")
        client_socket.sendall("False".encode())



def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")
    try:
        authenticated = False
        userid = None
        while not authenticated:
            authenticated, userid = authenticate(client_socket)
            response = str(authenticated)
            client_socket.sendall(response.encode())
            msg = client_socket.recv(BUFFER_SIZE).decode()
            if msg == "done" and authenticated:
                print(f"Client from {client_address} successfully logged in")
                with open('server.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    if csvfile.tell() == 0:
                        writer.writerow(["IP Address", "Port", "Status", "Timestamp"])
                    writer.writerow([client_address[0], client_address[1], "Logged in", datetime.now()])
                menuHandler(client_socket)
                break
            print(f"Client from {client_address} trying to login again")
    except ConnectionAbortedError:
        print(f"Connection with {client_address} aborted")
        with open('server.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                writer.writerow(["IP Address", "Port", "Status", "Timestamp"])
            writer.writerow([client_address[0], client_address[1], "Aborted", datetime.now()])
    finally:
        client_socket.close()
        print(f"Connection with {client_address} closed")
        with open('server.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if csvfile.tell() == 0:
                writer.writerow(["IP Address", "Port", "Status", "Timestamp"])
            writer.writerow([client_address[0], client_address[1], "Closed", datetime.now()])

if __name__ == "__main__":
    start_server()
