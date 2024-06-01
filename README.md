# Online Library Mangement System(Using Socket Programming)

## Configurations 
The following program is using TCP Connection.
```py
SERVER_PORT = 5050
BUFFER_SIZE = 2048
```

## 1.User Authentication
- **Client Code:**
```py
def login(userid, password, client_socket):
    authenticating_str = userid + "@" + password
    client_socket.sendall(authenticating_str.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    return response == "True"
```
- **Server Code:**

```py
def authenticate(client_socket):
    authentication_data = client_socket.recv(BUFFER_SIZE).decode().strip()
    if "@" not in authentication_data:
        return False, None  # Invalid authentication data format

    username, password = authentication_data.split("@")
    with open('students.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if str(row['username']) == username and str(row['password']) == password:
                return True

    return False, None
```

## 2.Admin Authentication

Admin password in stored in server.  
ADMIN_PASS = `ad123`

- **Client Code:**

```py
elif choice == 3:
            input_admin_pass = input("Enter admin password: ")
            print(input_admin_pass)
            msg = f"admin@{input_admin_pass}"
            client_socket.sendall(msg.encode())
            is_admin = client_socket.recv(BUFFER_SIZE).decode()
            if is_admin=="True":
                is_admin=True
            else:
                is_admin = False
```

- **Server Code:**

```py
def isAdmin(client_socket, admin_pass):
    if admin_pass == ADMIN_PASS:
        client_socket.sendall("True".encode())
    else:
        client_socket.sendall("False".encode())
```

## 3.Book Mangement

- **Client Code:**

```py
while True:
                    print("\n\n1.View Student Details")
                    print("2.Modify Book Details")
                    print("3.Add Book")
                    print("4.Delete Book")
                    print("5.Search Book")
                    print("6.Exit")
                    admin_choice = int(input())

                    if admin_choice == 1:
                        input_user_id = input("Enter student username: ")
                        msg = f"viewstudentdetails@{input_user_id}"
                        client_socket.sendall(msg.encode())
                        student_details = client_socket.recv(BUFFER_SIZE).decode()
                        print("\n\n")
                        print("****************************************************************************")
                        print(student_details)
                        print("****************************************************************************")
                    
                    elif admin_choice == 2:
                        modifyBook(client_socket)
                    
                    elif admin_choice == 3:
                        add_book(client_socket)
                        
                    elif admin_choice == 4:
                        book_id_to_delete = input("Enter the Book ID to delete: ")
                        msg = f"deletebook@{book_id_to_delete}"
                        client_socket.sendall(msg.encode())
                        delete_response = client_socket.recv(BUFFER_SIZE).decode()
                        print(delete_response)

                    elif admin_choice == 5:
                        while True:
                            print("Search book (by ID, title, author, or genre):")
                            search_parameter = input()
                            msg = f"searchbook@{search_parameter}"
                            client_socket.sendall(msg.encode())
                            msg = client_socket.recv(BUFFER_SIZE).decode()
                            print(msg)
                            print("\n\n")

                            continue_search = input("Do you want to search again? (yes/no): ")
                            if continue_search.lower() != 'yes':
                                break
                    
                    elif admin_choice == 6:
                        break

                    else:
                        print("\n\nInvalid choice. Please enter a valid option.\n\n")


def modifyBook(client_socket):
    print("Enter the Book ID of the book you want to modify:")
    book_id = input("Book ID: ")
    print("Which field do you want to modify? (title, author, genre, year, availability)")
    field = input("Field: ").lower()
    new_value = input(f"Enter new value for {field}: ")

    book_details = f"{book_id}@{field}@{new_value}"
    msg = f"modifybook@{book_details}"
    client_socket.sendall(msg.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    print(response)

def add_book(client_socket):
    print("Enter the following details to add a new book:")
    book_id = input("Book ID: ").strip()
    title = input("Title: ").strip()
    author = input("Author: ").strip()
    genre = input("Genre: ").strip()
    year = input("Year: ").strip()
    availability = input("Availability (Yes/No): ").strip()

    book_details = f"{book_id}@{title}@{author}@{genre}@{year}@{availability}"
    msg = f"addbook@{book_details}"
    client_socket.sendall(msg.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    print(response)
```  

- **Server Code:**

#### View Student Details

```py
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
```

#### Modify 

```py
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
```

#### Add book

```py
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
```

#### Delete Book

```py
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
```

#### Search

```py
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
```

## 4.File Locking

- **Server Code:**

```py
# Define a lock for file access
file_lock = threading.Lock()


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
```

## 5.Concurrent Access

- **Server Code:**

```py
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((SERVER_HOST, SERVER_PORT))
        server.listen()
        print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

        while True:
            client_socket, client_address = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
```
