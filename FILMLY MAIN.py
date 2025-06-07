# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 19:38:25 2024

@author: LENOVO
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import random
from datetime import datetime

# Initialize the database
connection = sqlite3.connect('database_name.db', timeout=10)  # Wait for 10 seconds if locked

cursor = connection.cursor()



# Create necessary tables
#creat upcoming movies
cursor.execute('''
CREATE TABLE IF NOT EXISTS UpcomingMovies (
    movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_name TEXT NOT NULL,
    release_date TEXT NOT NULL,
    genre TEXT NOT NULL
)
''')
# create onscreenmovies
cursor.execute('''
CREATE TABLE IF NOT EXISTS OnScreenMovies (
    movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_name TEXT NOT NULL,
    showtime TEXT NOT NULL,
    theater_name TEXT NOT NULL,
    date TEXT NOT NULL,
    screen_type TEXT NOT NULL,
    screen_number INTEGER NOT NULL
)
''')
# creat table to store customer booking
cursor.execute('''
CREATE TABLE IF NOT EXISTS CustomerBookings (
    customer_name TEXT NOT NULL,
    movie_id INTEGER NOT NULL,
    movie_name TEXT NOT NULL,
    showtime TEXT NOT NULL,
    theater_name TEXT NOT NULL,
    date TEXT NOT NULL,
    screen_type TEXT NOT NULL,
    screen_number INTEGER NOT NULL,
    booking_code INTEGER NOT NULL,
    upi_id TEXT DEFAULT NULL,
    payment_status TEXT NOT NULL,
    ticket_cost REAL NOT NULL,
    gst REAL NOT NULL,
    total_cost REAL NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES OnScreenMovies(movie_id)
)
''')

# Add this block to ensure the `payment_status` column exists with a default value
try:
    cursor.execute("""
    ALTER TABLE CustomerBookings 
    ADD COLUMN payment_status TEXT NOT NULL DEFAULT 'Unpaid';
    """)
except sqlite3.OperationalError:
    # Ignore the error if the column already exists
    pass


# Commit the changes
connection.commit()

# Create the main app class
class FilmlyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Filmly Movie Booking System")
        self.root.geometry("800x600")
        
        # Load the logo
        self.load_logo()

        # Display the main menu
        self.main_menu()
#creating a logo for main menu        
    def load_logo(self):
        logo_text = "𝔽𝕀𝕃𝕄𝕃𝕐"
        logo_label = tk.Label(self.root, text=logo_text, font=("Courier", 50, "bold"), fg="black", pady=10)
        logo_label.pack()
    
        subtitle_text = "Experience Cinema with Ease!"
        subtitle_label = tk.Label(self.root, text=subtitle_text, font=("Courier", 20, "bold"), fg="black", pady=5)
        subtitle_label.pack()
#function for main menu interface
    def main_menu(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        ttk.Label(frame, text="Welcome to Filmly", font=("Helvetica", 20)).pack(pady=10)

        ttk.Button(frame, text="Upcoming Movies", command=self.display_upcoming_movies, width=25).pack(pady=5)
        ttk.Button(frame, text="Movies Now Playing", command=self.display_now_playing_movies, width=25).pack(pady=5)
        ttk.Button(frame, text="Book Movie", command=self.book_movie, width=25).pack(pady=5)
        ttk.Button(frame, text="Check Booking Status", command=self.check_booking_status, width=25).pack(pady=5)
        ttk.Button(frame, text="Admin Panel", command=self.admin_panel, width=25).pack(pady=5)
        ttk.Button(frame, text="Exit", command=self.root.quit, width=25).pack(pady=5)
#function to display upcoming movies table
    def display_upcoming_movies(self):
        today = datetime.now().strftime('%Y-%m-%d')  
        cursor.execute(
            "SELECT movie_id, movie_name, release_date, genre FROM UpcomingMovies WHERE release_date > ?", (today,)
        )
        movies = cursor.fetchall()
        formatted_movies = [(movie[0], movie[1], movie[2], movie[3]) for movie in movies]
        self.show_popup(
            "Upcoming Movies",
            formatted_movies,
            ["Movie ID", "Movie Name", "Release Date", "Genre"]
        )
#function to display currently playing movies table
    def display_now_playing_movies(self):
        cursor.execute(
            """
            SELECT movie_id, movie_name, showtime, theater_name, date, screen_type, screen_number
            FROM OnScreenMovies
            """
        )
        movies = cursor.fetchall()
        if not movies:
            messagebox.showinfo("No Movies Now Playing", "There are no movies currently playing.")
            return
        formatted_movies = [
            (movie[0], movie[1], movie[2], movie[3], movie[4], movie[5], movie[6]) for movie in movies
        ]
        self.show_popup(
            "Now Playing Movies",
            formatted_movies,
            ["Movie ID", "Movie Name", "Showtime", "Theater Name", "Date", "Screen Type", "Screen Number"]
        )
#FUNCTION TO BOOK A MOVIE
    def book_movie(self):
        # Step 1: Get the customer's name
        name = simpledialog.askstring("Booking", "Enter your name:")
        if not name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return
    
        # Step 2: Display now playing movies and get the selected movie ID
        self.display_now_playing_movies()
        movie_id = simpledialog.askinteger("Booking", "Enter the Movie ID to book:")
        if not movie_id:
            messagebox.showerror("Error", "You must select a Movie ID.")
            return
    
        # Step 3: Get the number of seats for booking
        seats = simpledialog.askinteger("Booking", "Enter the number of seats:")
        if not seats or seats <= 0:
            messagebox.showerror("Error", "Invalid number of seats.")
            return
        
        # Step 4: Calculate total cost (including GST)
        seat_cost = 150
        total_cost = round(seats * seat_cost * 1.18, 2)  # Including 18% GST
        gst = round(total_cost - (seats * seat_cost), 2)
    
        # Step 5: Choose the payment method (UPI or Theater)
        payment_method = simpledialog.askstring("Payment", "Choose Payment Method (UPI/Theater):")
        if not payment_method or payment_method.lower() not in ["upi", "theater"]:
            messagebox.showerror("Error", "Invalid payment method. Choose 'UPI' or 'Theater'.")
            return
    
        # Step 6: Handle UPI payment method
        if payment_method.lower() == "upi":
            admin_upi = "admin@bank"
            messagebox.showinfo("UPI Payment", f"Please pay ₹{total_cost} to the UPI ID: {admin_upi}")
            transaction_id = simpledialog.askstring("Payment", "Enter the UPI Transaction ID:")
            if not transaction_id:
                messagebox.showerror("Error", "Transaction ID is required for UPI payment.")
                return
            payment_status = "Unpaid"
        else:
            transaction_id = "Payment on Theater"
            payment_status = "Not Paid"
        
        # Step 7: Generate booking code and get current date
        booking_code = str(random.randint(1000, 9999))
        current_date = datetime.now().strftime("%Y-%m-%d")
    
        # Step 8: Save the booking details to the database
        cursor.execute('''INSERT INTO CustomerBookings 
    (customer_name, movie_id, movie_name, showtime, theater_name, date, screen_type, screen_number, 
    booking_code, upi_id, payment_status, ticket_cost, gst, total_cost) 
    SELECT ?, movie_id, movie_name, showtime, theater_name, ?, screen_type, screen_number, ?, ?, ?, ?, ?, ?
    FROM OnScreenMovies WHERE movie_id = ?''',
    (name, current_date, booking_code, transaction_id, "Unpaid", total_cost, gst, total_cost, movie_id))
        # Step 9: Prepare the ticket detailsS
        ticket = (
            "\n"
            "╔═══════════════════════════════════════════╗\n"
            "║               MOVIE TICKET                ║\n"
            "╠═══════════════════════════════════════════╣\n"
           f"║ Name           : {name:<30}               ║\n"
           f"║ Movie ID       : {movie_id:<30}           ║\n"
           f"║ Seats          : {seats:<30}              ║\n"
           f"║ Total Cost     : ₹{total_cost:<28}        ║\n"
           f"║ GST Included   : ₹{gst:<28}               ║\n"
           f"║ Payment Status : {payment_status:<26}     ║\n"
           f"║ Transaction ID : {transaction_id:<26}     ║\n"
           f"║ Booking Code   : {booking_code:<27}       ║\n"
            "╠═══════════════════════════════════════════╣\n"
            "║        THANK YOU FOR YOUR BOOKING!        ║\n"
            "║        ENJOY YOUR MOVIE EXPERIENCE        ║\n"
            "╚═══════════════════════════════════════════╝\n"
           f" ╔════════════════════════════════════════════╗\n"
           f" ║           IMPORTANT BOOKING INFO           ║\n"
           f" ╠════════════════════════════════════════════╣\n"
           f" ║ UPI Payment:                               ║\n"
           f" ║ If you chose UPI as your payment method,   ║\n"
           f" ║ your payment status will update within a   ║\n"
           f" ║ few minutes.                               ║\n"
           f" ╠════════════════════════════════════════════╣\n"
           f" ║ Theater Payment:                           ║\n"
           f" ║ Please ensure your tickets are paid for    ║\n"
           f" ║ at least 1 hour before the movie start     ║\n"
           f" ║ time. Unpaid tickets will be canceled and  ║\n"
           f" ║ offered to other customers.                ║\n"
           f" ╠════════════════════════════════════════════╣\n"
          

            
        )

        # Step 10: Show the ticket and booking confirmation message
        messagebox.showinfo("Your Ticket", ticket)
        messagebox.showinfo("Booking Completed", f"Your booking is confirmed!\nBooking Code: {booking_code}\nKeep this code for future reference.")
# function to check booking status (for upi payments)
    def check_booking_status(self):
        name = simpledialog.askstring("Booking Status", "Enter your name:")
        if not name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return
        booking_code = simpledialog.askstring("Booking Status", "Enter your booking code:")
        if not booking_code:
            messagebox.showerror("Error", "Booking code cannot be empty.")
            return
        cursor.execute('''SELECT customer_name, movie_name, showtime, theater_name, date, screen_type, 
                                  screen_number, booking_code, payment_status, total_cost 
                          FROM CustomerBookings 
                          WHERE customer_name = ? AND booking_code = ?''', (name, booking_code))
        booking = cursor.fetchone()
        if booking:
            status_message = (
                
                    "\n"
                    "╔════════════════════════════════════════════════════╗\n"
                    "║                BOOKING STATUS                      ║\n"
                    "╠════════════════════════════════════════════════════╣\n"
                    f"║ Name              : {booking[0]:<30}              ║\n"
                    f"║ Movie             : {booking[1]:<30}              ║\n"
                    f"║ Showtime          : {booking[2]:<30}              ║\n"
                    f"║ Theater           : {booking[3]:<30}              ║\n"
                    f"║ Date              : {booking[4]:<30}              ║\n"
                    f"║ Screen Type       : {booking[5]:<30}              ║\n"
                    f"║ Screen Number     : {booking[6]:<30}              ║\n"
                    f"║ Booking Code      : {booking[7]:<30}              ║\n"
                    f"║ Payment Status    : {booking[8]:<30}              ║\n"
                    f"║ Total Cost        : ₹{booking[9]:<28}             ║\n"
                    "╠════════════════════════════════════════════════════╣\n"
                    "║      THANK YOU FOR YOUR BOOKING!                   ║\n"
                    "║    WE HOPE YOU ENJOY YOUR MOVIE EXPERIENCE!        ║\n"
                    "╚════════════════════════════════════════════════════╝\n"
                    f" ╔════════════════════════════════════════════╗\n"
                    f" ║           IMPORTANT BOOKING INFO           ║\n"
                    f" ╠════════════════════════════════════════════╣\n"
                    f" ║ UPI Payment:                               ║\n"
                    f" ║ If you chose UPI as your payment method,   ║\n"
                    f" ║ your payment status will update within a   ║\n"
                    f" ║ few minutes.                               ║\n"
                    f" ╠════════════════════════════════════════════╣\n"
                    f" ║ Theater Payment:                           ║\n"
                    f" ║ Please ensure your tickets are paid for    ║\n"
                    f" ║ at least 1 hour before the movie start     ║\n"
                    f" ║ time. Unpaid tickets will be canceled and  ║\n"
                    f" ║ offered to other customers.                ║\n"
                    f" ╠════════════════════════════════════════════╣\n"
                )

            messagebox.showinfo("Booking Information", status_message)
        else:
            messagebox.showerror("Error", "No booking found with the given details.")
# Main Application Class
# to check the user is authorised to admin interface (PASSWORD:admin123)
    def admin_panel(self):
        password = simpledialog.askstring("Admin Login", "Enter Admin Password:", show="*")
        if password == "admin123":  # Example password
            self.show_admin_panel_menu()
        else:
            messagebox.showerror("Error", "Incorrect password.")
#function to display admin pannel
    def show_admin_panel_menu(self):
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin Panel")
        admin_window.geometry("600x400")

        ttk.Label(admin_window, text="Admin Panel", font=("Helvetica", 20)).pack(pady=20)

        # Admin options as buttons
        ttk.Button(admin_window, text="View All Bookings", command=self.display_all_bookings, width=25).pack(pady=10)
        ttk.Button(admin_window, text="Update Payment Status", command=self.update_payment_status, width=25).pack(pady=10)
        ttk.Button(admin_window, text="Delete Incorrect Booking", command=self.delete_incorrect_booking, width=25).pack(pady=10)
        ttk.Button(admin_window, text="Modify Movies", command=self.modify_movies, width=25).pack(pady=10)
        ttk.Button(admin_window, text="Back to Main Menu", command=admin_window.destroy, width=25).pack(pady=10)
#function to display all bookings
    def display_all_bookings(self):
        cursor.execute("SELECT * FROM CustomerBookings")
        bookings = cursor.fetchall()
    
        self.show_popup("All Bookings", bookings, [
            "Customer Name", "Movie ID", "Movie Name", "Showtime", "Theater Name", 
            "Date","Booking Status", "Screen Type", "Screen Number", "Booking Code", 
            "UPI ID", "Ticket Cost", "GST", "Total Cost"
        ])
#function to check payment status (for upi payments)
    def update_payment_status(self):
        try:
            cursor.execute("SELECT * FROM CustomerBookings")
            bookings = cursor.fetchall()
    
            popup_window = tk.Toplevel(self.root)
            popup_window.title("Verify Payment Status")
    
            tree = ttk.Treeview(popup_window, columns=("Customer Name", "Movie ID", "Movie Name", "Showtime",
            "Theater Name", "Date", "Screen Type", "Screen Number", "Booking Code", "UPI ID", "Payment_Status",
            "Ticket Cost", "GST", "Total Cost"), show="headings")
            headers = ["Customer Name", "Movie ID", "Movie Name", 
            "Showtime", "Theater Name", "Date", "Screen Type", "Screen Number", "Booking Code", 
            "UPI ID", "Payment_Status", "Ticket Cost", "GST", "Total Cost"]
            for header in headers:
                tree.heading(header, text=header)
                tree.column(header, width=150)
    
            for row in bookings:
                tree.insert("", "end", values=row)
    
            tree.pack(fill=tk.BOTH, expand=True)
#modifiying payment status    
            def update_selected():
                selected_item = tree.selection()
                if selected_item:
                    booking_code = tree.item(selected_item[0], "values")[8]  # Booking Code index is 8
                    new_status = simpledialog.askstring("Update Payment", "Enter new payment status (Paid/Unpaid):")
    
                    if new_status:
                        new_status = new_status.strip().capitalize()  # Capitalize input
                        if new_status in ["Paid", "Unpaid"]:
                            try:
                                cursor.execute("SELECT * FROM CustomerBookings WHERE booking_code = ?", (booking_code,))
                                result = cursor.fetchone()
                                if result:
                                    cursor.execute("UPDATE CustomerBookings SET Payment_Status = ? WHERE booking_code = ?", (new_status, booking_code))
                                    connection.commit()
                                    messagebox.showinfo("Success", "Payment status updated successfully!")
                                    popup_window.destroy()
                                    self.update_payment_status()  # Reload updated table
                                else:
                                    messagebox.showerror("Error", "Booking not found.")
                            except Exception as e:
                                messagebox.showerror("Error", f"Failed to update payment status: {e}")
                        else:
                            messagebox.showerror("Error", "Invalid payment status. Please enter 'Paid' or 'Unpaid'.")
                    else:
                        messagebox.showerror("Error", "Payment status cannot be empty.")
                else:
                    messagebox.showerror("Error", "No booking selected.")
    
            ttk.Button(popup_window, text="Update Payment Status", command=update_selected).pack(pady=10)
            ttk.Button(popup_window, text="Close", command=popup_window.destroy).pack(pady=10)
    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bookings: {e}")
#to select false booking for deletion
    def delete_incorrect_booking(self):
        try:
            # Create a new popup window to show bookings
            popup_window = tk.Toplevel(self.root)
            popup_window.title("Select Booking to Delete")
    
            # Create Treeview to display bookings
            tree = ttk.Treeview(popup_window, columns=("Customer Name", "Movie ID", "Movie Name", "Showtime", 
                                                       "Theater Name", "Date", "Screen Type", "Screen Number", 
                                                       "Booking Code", "UPI ID", "Payment_Status", "Ticket Cost",
                                                       "GST", "Total Cost"), show="headings")
            
            headers = ["Customer Name", "Movie ID", "Movie Name", "Showtime", "Theater Name", "Date", "Screen Type", 
                       "Screen Number", "Booking Code", "UPI ID", "Payment_Status", "Ticket Cost", "GST", "Total Cost"]
            for header in headers:
                tree.heading(header, text=header)
                tree.column(header, width=150)
    
            # Fetch all bookings from the database
            cursor.execute("SELECT * FROM CustomerBookings")
            bookings = cursor.fetchall()
    
            # Insert fetched bookings into the treeview
            for row in bookings:
                tree.insert("", "end", values=row)
    
            tree.pack(fill=tk.BOTH, expand=True)
# to delete selected booking    
            def delete_selected():
                selected_item = tree.selection()
                if selected_item:
                    # Get the booking code from the selected item
                    booking_code = tree.item(selected_item[0], "values")[8]  # Booking Code index is 8
    
                    # Fetch the selected booking details
                    cursor.execute("SELECT * FROM CustomerBookings WHERE booking_code = ?", (booking_code,))
                    booking = cursor.fetchone()
    
                    if booking:
                        # Ask for confirmation before deleting the booking
                        confirmation = messagebox.askyesno("Confirmation", f"Are you sure you want to delete the booking for {booking[0]} (Customer Name: {booking[0]}, Movie: {booking[2]}, Showtime: {booking[3]}, Theater: {booking[4]})?")
                                                           
                        if confirmation:
                            # Delete the selected booking from the database
                            cursor.execute("DELETE FROM CustomerBookings WHERE booking_code = ?", (booking_code,))
                            connection.commit()
                            messagebox.showinfo("Success", "Booking deleted successfully!")
                            popup_window.destroy()  # Close the popup window after deletion
                            self.update_payment_status()  # Refresh the booking list in the main window
                        else:
                            messagebox.showinfo("Canceled", "Booking deletion canceled.")
                    else:
                        messagebox.showerror("Error", "Booking not found.")
                else:
                    messagebox.showerror("Error", "No booking selected.")
    
            # Add a button to trigger the deletion of the selected booking
            ttk.Button(popup_window, text="Delete Selected Booking", command=delete_selected).pack(pady=10)
    
            # Add a button to close the popup window
            ttk.Button(popup_window, text="Close", command=popup_window.destroy).pack(pady=10)
    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bookings: {e}")
# function to show interface to modify both tables
    def modify_movies(self):
        modify_window = tk.Toplevel(self.root)
        modify_window.title("Modify Movies")
        modify_window.geometry("400x300")

        ttk.Button(modify_window, text="Upcoming Movies", command=self.modify_upcoming_movies, width=25).pack(pady=10)
        ttk.Button(modify_window, text="Movies Now Playing", command=self.modify_now_playing_movies, width=25).pack(pady=10)
        ttk.Button(modify_window, text="Back", command=modify_window.destroy, width=25).pack(pady=10)
# interface to modify upcoming movies
    def modify_upcoming_movies(self):
        modify_window = tk.Toplevel(self.root)
        modify_window.title("Modify Upcoming Movies")
        modify_window.geometry("400x300")

        ttk.Button(modify_window, text="Update", command=self.update_upcoming_movie, width=25).pack(pady=10)
        ttk.Button(modify_window, text="Show", command=self.display_upcoming_movies, width=25).pack(pady=10)
        ttk.Button(modify_window, text="Delete", command=self.delete_upcoming_movie, width=25).pack(pady=10)
        ttk.Button(modify_window, text="Back", command=modify_window.destroy, width=25).pack(pady=10)
# interface to modify onplaying movies
    def modify_now_playing_movies(self):
        modify_window = tk.Toplevel(self.root)
        modify_window.title("Modify Movies Now Playing")
        modify_window.geometry("400x300")

        ttk.Button(modify_window, text="Update now_playing_movies", command=self.update_now_playing_movie, width=25).pack(pady=10)
        ttk.Button(modify_window, text="Show now_playing_movies", command=self.display_now_playing_movies, width=25).pack(pady=10)
        ttk.Button(modify_window, text="Delete now_playing_movies", command=self.delete_now_playing_movie, width=25).pack(pady=10)
        ttk.Button(modify_window, text="Back", command=modify_window.destroy, width=25).pack(pady=10)

    def show_popup(self, title, data, headers):
        # Create the popup window
        popup_window = tk.Toplevel(self.root)
        popup_window.title(title)
        
        # Create a Frame to hold the Treeview and Scrollbars
        frame = tk.Frame(popup_window)
        frame.pack(fill=tk.BOTH, expand=True)
    
        # Create the Treeview with the given headers
        tree = ttk.Treeview(frame, columns=headers, show="headings")
        
        # Set up the columns and their widths
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, width=150, anchor="w")  # Adjust width as needed
        
        # Insert the data into the Treeview
        for row in data:
            tree.insert("", "end", values=row)
        
        # Create vertical scrollbar
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)
        
        # Create horizontal scrollbar
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        hsb.pack(side="bottom", fill="x")
        tree.configure(xscrollcommand=hsb.set)
        
        # Pack the treeview into the frame
        tree.pack(fill=tk.BOTH, expand=True)
    
        # Button to close the popup window
        ttk.Button(popup_window, text="Close", command=popup_window.destroy).pack(pady=10)

# function  add uopcomming movies
    def update_upcoming_movie(self):
        movie_name = simpledialog.askstring("Add Upcoming Movie", "Enter movie name:")
        release_date = simpledialog.askstring("Add Upcoming Movie", "Enter release date (YYYY-MM-DD):")
        genre = simpledialog.askstring("Add Upcoming Movie", "Enter genre:")
        
        if movie_name and release_date and genre:
            try:
                cursor.execute('''
                    INSERT INTO UpcomingMovies (movie_name, release_date, genre)
                    VALUES (?, ?, ?)
                ''', (movie_name, release_date, genre))
                connection.commit()
                messagebox.showinfo("Success", "New upcoming movie added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add movie: {str(e)}")
        else:
            messagebox.showerror("Error", "All fields are required to add a new movie.")
# show upcoming movies table to delete a movie
    def delete_upcoming_movie(self):
        try:
            # Create a new popup window to show upcoming movies
            popup_window = tk.Toplevel(self.root)
            popup_window.title("Select Movie to Delete")
    
            # Create Treeview to display upcoming movies
            tree = ttk.Treeview(popup_window, columns=("Movie ID", "Movie Name", "Director", 
                                                       "Genre", "Release Date",
                                                       "Duration", "Rating"), show="headings")
            
            headers = ["Movie ID", "Movie Name", "Director", 
                       "Genre", "Release Date", "Duration", "Rating"]
            for header in headers:
                tree.heading(header, text=header)
                tree.column(header, width=150)
    
            # Fetch all upcoming movies from the database
            cursor.execute("SELECT * FROM UpcomingMovies")
            movies = cursor.fetchall()
    
            # Insert fetched movies into the treeview
            for row in movies:
                tree.insert("", "end", values=row)
    
            tree.pack(fill=tk.BOTH, expand=True)
 # delete selected upcoming movies   
            def delete_selected():
                selected_item = tree.selection()
                if selected_item:
                    # Get the movie name from the selected item
                    movie_name = tree.item(selected_item[0], "values")[1]  # Movie Name index is 1
    
                    # Fetch the selected movie details
                    cursor.execute("SELECT * FROM UpcomingMovies WHERE movie_name = ?", (movie_name,))
                    movie = cursor.fetchone()
    
                    if movie:
                        # Ask for confirmation before deleting the movie
                        confirmation = messagebox.askyesno("Confirm Deletion", f"Are you sure to delete the movie '{movie_name}'?")
    
                        if confirmation:
                            # Delete the selected movie from the database
                            cursor.execute("DELETE FROM UpcomingMovies WHERE movie_name = ?", (movie_name,))
                            connection.commit()
                            messagebox.showinfo("Success", "Movie deleted successfully!")
                            popup_window.destroy()  # Close the popup window after deletion
                            self.update_upcoming_movies()  # Refresh the upcoming movies list in the main window
                        else:
                            messagebox.showinfo("Cancelled", "Movie deletion cancelled.")
                    else:
                        messagebox.showerror("Error", "Movie not found.")
                else:
                    messagebox.showerror("Error", "No movie selected.")
    
            # Add a button to trigger the deletion of the selected movie
            ttk.Button(popup_window, text="Delete Selected Movie", command=delete_selected).pack(pady=10)
    
            # Add a button to close the popup window
            ttk.Button(popup_window, text="Close", command=popup_window.destroy).pack(pady=10)
    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load movies: {e}")
#add onscreen movies
    def update_now_playing_movie(self):
        title = simpledialog.askstring("Add Now Playing Movie", "Enter movie title:")
        showtime = simpledialog.askstring("Add Now Playing Movie", "Enter showtime (HH:MM):")
        theater_name = simpledialog.askstring("Add Now Playing Movie", "Enter theater name:")
        date = simpledialog.askstring("Add Now Playing Movie", "Enter date (YYYY-MM-DD):")
        screen_type = simpledialog.askstring("Add Now Playing Movie", "Enter screen type:")
        screen_number = simpledialog.askinteger("Add Now Playing Movie", "Enter screen number:")
    
        if title and showtime and theater_name and date and screen_type and screen_number:
            try:
                cursor.execute('''
                    INSERT INTO OnScreenMovies (movie_name, showtime, theater_name, date, screen_type, screen_number)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (title, showtime, theater_name, date, screen_type, screen_number))
                connection.commit()
                messagebox.showinfo("Success", "New 'Now Playing' movie added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add movie: {str(e)}")
        else:
            messagebox.showerror("Error", "All fields are required to add a new movie.")
#display onscreen movies table to delet
    def delete_now_playing_movie(self):
        try:
            # Create a new popup window
            popup_window = tk.Toplevel(self.root)
            popup_window.title("Select Movie to Delete")
    
            # Create Treeview for displaying movies
            tree = ttk.Treeview(
                popup_window,
                columns=("Movie Name", "Movie ID", "Showtime", "Genre", "Director", "Duration", "Rating"),
                show="headings",
            )
            
            headers = ["Movie Name", "Movie ID", "Showtime", "Genre", "Director", "Duration", "Rating"]
            for header in headers:
                tree.heading(header, text=header)
                tree.column(header, width=150)
    
            # Fetch movies from the database
            cursor.execute("SELECT * FROM OnScreenMovies")
            movies = cursor.fetchall()
            for row in movies:
                tree.insert("", "end", values=row)
            tree.pack(fill=tk.BOTH, expand=True)
 # to delete selected movie in onscreen table   
            def delete_selected():
                selected_item = tree.selection()
                if selected_item:
                    # Get movie details from the selected row
                    row_values = tree.item(selected_item[0], "values")
                    print("Selected row values:", row_values)  # Debugging the selected row values
                    movie_id = row_values[0]  # Assuming movie_id is in the first column, adjust if needed
                    print("Using Movie ID for query:", movie_id)  # Debugging
    
                    try:
                        # Fetch movie details from the database using the selected movie_id
                        cursor.execute("SELECT * FROM OnScreenMovies WHERE movie_id = ?", (movie_id,))
                        movie = cursor.fetchone()
                        print("Fetched movie:", movie)  # Debugging the movie fetched
    
                        if movie:
                            # Ask for confirmation before deleting the movie
                            confirmation = messagebox.askyesno(
                                "Confirm Deletion",
                                f"Are you sure you want to delete the movie '{movie[1]}' (Movie ID: {movie_id})?",
                            )
                            if confirmation:
                                # Delete movie from the database
                                cursor.execute("DELETE FROM OnScreenMovies WHERE movie_id = ?", (movie_id,))
                                connection.commit()
                                messagebox.showinfo("Success", "Movie deleted successfully!")
                                popup_window.destroy()
                                self.update_now_playing_movies()  # Update the main window to reflect changes
                            else:
                                messagebox.showinfo("Cancelled", "Movie deletion cancelled.")
                        else:
                            messagebox.showerror("Error", f"Movie with ID '{movie_id}' not found in the database.")
                    except Exception as fetch_error:
                        messagebox.showerror("Error", f"Error during database operation: {fetch_error}")
                else:
                    messagebox.showerror("Error", "No movie selected.")
    
            # Add a button to delete the selected movie
            ttk.Button(popup_window, text="Delete Selected Movie", command=delete_selected).pack(pady=10)
            # Add a button to close the popup window
            ttk.Button(popup_window, text="Close", command=popup_window.destroy).pack(pady=10)
    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load now playing movies: {e}")




# Run the app
root = tk.Tk()
app = FilmlyApp(root)
root.mainloop()

# Close the database connection on exit
connection.close()
