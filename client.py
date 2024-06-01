import socket

# Server configuration
SERVER_HOST = socket.gethostname()  # Get the hostname dynamically
SERVER_PORT = 5050
BUFFER_SIZE = 2048

def start_client(client_socket):
    print("\n\n......................Welcome to OLMS.......................\n\n")

    while True:   
        print("\n\nEnter 1 for login and 0 for exit")
        option = int(input())
        
        if option == 1:
            userid = input("Username:")
            password = input("Password:")
            
            if login(userid, password, client_socket):
                client_socket.send("done".encode())
                clientMenu(client_socket, userid)
                break
            else:
                print("\n\nWrong details entered, Please try again")
                client_socket.send("wait".encode())
                continue
        
        elif option == 0:
            client_socket.close()
            exit()

        else:
            print("\n\nPlease enter a valid number")

def login(userid, password, client_socket):
    authenticating_str = userid + "@" + password
    client_socket.sendall(authenticating_str.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    return response == "True"

def clientMenu(client_socket, userid):
    print("\n\n\n\n")
    print("****************************************************************************")
    print("                           Welcome to Student Panel                    ")
    print("****************************************************************************")

    while True:
        print("\n\n1.Show Borrowed Books")
        print("\n\n2.Borrow Book")
        print("\n\n3.Admin Controls")
        print("\n\n4.Exit\n\n")
    
        choice = int(input())

        if choice == 1:
            msg = f"borrowedbooks@{userid}"
            client_socket.sendall(msg.encode())
            borrow_books = client_socket.recv(BUFFER_SIZE).decode()
            print("\n\n")
            print("****************************************************************************")
            print(borrow_books)
            print("\n\n")
            print("****************************************************************************")

        elif choice == 2:
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

            print("\n\nEnter book id (enter 0 for not borrowing)")
            book_id = input()
            if int(book_id) != 0:
                msg = f"borrowbook@{userid}@{book_id}"
                client_socket.sendall(msg.encode())
                msg = client_socket.recv(BUFFER_SIZE).decode()
                print(msg)

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

            if is_admin:
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
            else:
                print("Invalid admin password.")
                continue

        elif choice == 4:
            client_socket.close()
            exit()

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



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))
start_client(client_socket)
