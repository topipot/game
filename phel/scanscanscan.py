class ScanUser:
    def __init__(self, parent_window=None):
        self.parent_window = parent_window

        self.window = tk.Toplevel(parent_window)
        self.window.title("Scan User ID")

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 550)  
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)  

        self.canvas = tk.Canvas(self.window, width=640, height=480)
        self.canvas.pack()

        self.qr_detected = False
        self.scanned_id = ''

        self.qr_scanid_label = Label(self.window, text="Username: ")
        self.qr_scanid_label.pack()

        self.scan_button = Button(self.window, text="Scan ID", command=self.scan_id)
        self.scan_button.pack()

        self.done_button = Button(self.window, text="Done", command=self.done, state="disabled")
        self.done_button.pack()

        self.scanned_id_label = Label(self.window,text=self.scanned_id)
        self.scanned_id_label.pack_forget()
 
        self.capture_running = True
        self.update()
    
    def open(self):
        qrcodescanner = QRCodeScanner(self.done)

    def get_scanuser(self):
        return self.scanuser

    def scan_id(self):
        if self.qr_detected:
            self.qr_scanid_label.config(text=f"Username: {self.scanned_id}")
            self.scanuser = self.scanned_id
            print(self.scanuser)

            try:
                with sshtunnel.SSHTunnelForwarder(
                ('ssh.pythonanywhere.com'),
                ssh_username='wonderpets', ssh_password='Bo0kLocator!',
                remote_bind_address=('wonderpets.mysql.pythonanywhere-services.com', 3306)
            ) as tunnel:
                    connection = MySQLdb.connect(
                        user='wonderpets',
                        passwd='chocolate290',
                        host='127.0.0.1', port=tunnel.local_bind_port,
                        db='wonderpets$db_library',
                    )

                    cursor = connection.cursor()

                    cursor.execute("SELECT username FROM userss WHERE username = %s", (self.scanned_id,))
                    user = cursor.fetchone()

                    if not user:
                        messagebox.showwarning("Warning", "Username not found.")
                    
                    else:
                        print('Username exists')
                        self.scan_button.config(state="disabled")
                        self.done_button.config(state="active")

                        
                    cursor.close()
                    connection.close()

            except Exception as e:
                print("Error fetching data from database:", str(e))


    def update(self):
        ret, frame = self.camera.read()
        if ret:
            decoded_objects = decode(frame)
            if decoded_objects:
                x, y, w, h = decoded_objects[0].rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                self.qr_detected = True
                self.scanned_id = decoded_objects[0].data.decode('utf-8')
            else:
                self.qr_detected = False
                self.scanned_id = ""

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.photo = photo

        if self.capture_running:
            self.window.after(30, self.update)
        else:
            self.camera.release()

    def close_window(self):
        self.capture_running = False
        self.window.destroy()
        self.camera.release()

    def back_to_first_window(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the methods window?")
        
        if asktoproceed:
            self.window.destroy()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.parent_window.deiconify()
    
    def open_first_window(self):
        self.window.withdraw()  
        first_window = FirstWindow(self.window)
        first_window.show_scanuser_label(self.scanuser)

    def done(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the methods windows?")
        
        if asktoproceed:
            
            #self.window.destroy()
            self.open_first_window()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            #self.parent_window.deiconify()
        else:
            ask_to_scan_again = messagebox.askyesno("Scan Again", "Do you want to scan again?")
            if ask_to_scan_again:
                self.scan_button.config(state="active")
                self.done_button.config(state="disabled")
                self.scan_id()  
            else:
                pass  

class QRCodeScanner:
    def __init__(self, parent_window=None, selected_shelf=""):
        self.parent_window = parent_window
        self.selected_shelf = selected_shelf

        # self.user_instance = ScanUser()
        # self.scan_user_instance = ScanUser(parent_window=self.parent_window)
        # # Accessing the scanned_id attribute directly from the instance
        # self.scanned_id = self.scan_user_instance.get_scanned_id()

        # self.scanned_id= ScanUser.scanned_id
        
        self.window = tk.Toplevel(parent_window)
        self.window.title("QR Code Scanner")

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 550)  # Set the width to 1920 pixels
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)  # Set the height to 1080 pixels

        self.canvas = tk.Canvas(
            self.window,
            bg="#ffffff",
            height=480,
            width=640, 
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        self.canvas.pack()


        self.results_label = Label(self.window, text="Scanning QR codes...")
        self.results_label.place(x =260 , y = 400)
        self.combo_box_value = tk.StringVar()  # Variable to store the selected combo box value

        # Create a label to display the combo box value
        self.combo_box_label = Label(self.window, textvariable=self.combo_box_value)
        self.combo_box_label.pack()
        
        self.selected_shelf_label = Label(self.window, text=f"Selected Shelf: {self.selected_shelf}")  # Display selected shelf
        self.selected_shelf_label.pack_forget()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        img5 = PhotoImage(file=os.path.join(script_dir, "stopCam.png"))
        self.stopCam = Button(
            self.canvas,
            image=img5,
            borderwidth=0,
            highlightthickness=0,
            command=self.close_window,
            relief="flat"
        )
        self.stopCam.place(x =200 , y = 450, width = 232, height = 30)
        self.stopCam.image=img5    
       
        self.stop_button = Button(self.window, text="Stop Camera", command=self.close_window)
        self.stop_button.pack()

        self.back_button = Button(self.window, text="Back to First Window", command=self.back_to_first_window)
        self.back_button.pack()

        self.qr_values = self.retrieve_data(self.selected_shelf)  
        self.camera_running = True

        self.red_qr_codes = set()

        self.update()

        self.start_datetime = datetime.now()
        self.stop_datetime = None

    def update_stop_datetime(self):
        self.stop_datetime = datetime.now()

    def red_codes (self):
        self.length = len(self.red_qr_codes)
        a = self.length
        return a

    def retrieve_data(self, selected_shelf):
        try:
            base_url = "https://wonderpets.pythonanywhere.com/"
            shelf_url = base_url + selected_shelf
            response = requests.get(shelf_url)
            print("API RESPONSE:", response.json())
            if response.status_code == 200:
                qr_values = response.json()
                return set(qr_values)
            else:
                print("Error fetching data from API:", response.text)
                return set()
        except Exception as e:
            print("Error fetching data from API:", str(e))
            return set()

    def update(self):
        # self.update_date_time()

        ret, frame = self.camera.read()
        if ret:
            decoded_objects = decode(frame)
            self.show_frame(frame, decoded_objects)
        self.window.after(30, self.update)

    def close_window(self):
        print('wow')
        asktoproceed = messagebox.askyesno("Confirmation", "Done scanning?")
        if asktoproceed:
            self.update_stop_datetime()
            self.insert_misplaced()
            ask = messagebox.askyesno("Confirmation", "Scan Again?")
            if ask: 
                self.camera_running = False
                if self.camera.isOpened():
                    self.camera.release()
                self.open_combobox()
            else:
                self.update_date_time() 

    def open_combobox(self):
        self.window.withdraw()
        MainApplication(self.window)
       
    def show_frame(self, frame, decoded_objects):
        for obj in decoded_objects:
            x, y, w, h = obj.rect
            qr_data = obj.data.decode('utf-8')

            if qr_data in self.qr_values:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, qr_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, qr_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                self.red_qr_codes.add(qr_data)
                print(self.red_qr_codes)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.photo = photo

    def insert_misplaced(self):
        try:
            with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='wonderpets', ssh_password='Bo0kLocator!',
            remote_bind_address=('wonderpets.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
                connection = MySQLdb.connect(
                    user='wonderpets',
                    passwd='chocolate290',
                    host='127.0.0.1', port=tunnel.local_bind_port,
                    db='wonderpets$db_library',
                )

                cursor = connection.cursor()

                red_code_length = self.red_codes()

                #insert to database
                insert_query = "INSERT INTO log_read (username, misplaced_books, date_startscan, date_stopscan) VALUES (%s,%s, %s, %s)"
                data_to_insert = (
                    self.scanned_id, 
                    red_code_length , 
                    self.start_datetime.strftime('%Y-%m-%d %H:%M:%S'), 
                    self.stop_datetime.strftime('%Y-%m-%d %H:%M:%S')
                    ) 
                cursor.execute(insert_query, data_to_insert)
                connection.commit()
                print('Successfully inserted')

                cursor.close()
                connection.close()

        except Exception as e:
            print("Error fetching data from database:", str(e))

    # def user_id(self):
    #     a = ScanUser.scanned_id()
    #     return a

    def back_to_first_window(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the first window?")
        
        if asktoproceed:
            self.window.destroy()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.parent_window.deiconify()
            self.update_date_time() 

    

class Borrow:
    def __init__(self, parent_window=None):
        self.parent_window = parent_window

        self.window = tk.Toplevel(parent_window)
        self.window.title("Borrow")

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 550)  
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)  

        self.canvas = tk.Canvas(self.window, width=640, height=480)
        self.canvas.pack()

        self.qr_detected = False
        self.qr_databorrowers = "" 
        self.qr_data = ""

        self.wow_label = Label(self.window, text="")
        self.wow_label.pack_forget()

        self.qr_borrower_label = Label(self.window, text="Borrower:")
        self.qr_borrower_label.pack()

        self.qr_data_label = Label(self.window, text="QR Code Data: ")
        self.qr_data_label.pack()

        self.borrower_button = Button(self.window, text="Scan Borrower", command=self.borrower_qr_code)
        self.borrower_button.pack()

        self.borrow_button = Button(self.window, text="Scan Borrowed Book", command=self.borrow_qr_code, state="disabled")
        self.borrow_button.pack()

        self.back_button = Button(self.window, text="Back to First Window", command=self.back_to_first_window)
        self.back_button.pack()

        self.capture_running = True
        self.update()

    def borrower_qr_code(self):
        if self.qr_detected:
            self.qr_borrower_label.config(text=f"Borrower: {self.qr_databorrowers}")
            
            # Enable the borrow_button and disable the borrower_button
            self.borrow_button.config(state="normal")
            self.borrower_button.config(state="disabled")

        
    def borrow_qr_code(self):
        if self.qr_detected:
            self.qr_data_label.config(text=f"QR Code Data: {self.qr_data}")

        return_date = current_date + timedelta(days=3)
        formatted_return_date = return_date.strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='wonderpets', ssh_password='Bo0kLocator!',
            remote_bind_address=('wonderpets.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
                connection = MySQLdb.connect(
                    user='wonderpets',
                    passwd='chocolate290',
                    host='127.0.0.1', port=tunnel.local_bind_port,
                    db='wonderpets$db_library',
                )

                cursor = connection.cursor()

                #get quantity of the book_id detected
                cursor.execute("SELECT quantity FROM gen_books WHERE book_id = %s", (self.qr_data,))
                cur_quan = cursor.fetchone()

                if cur_quan:
                    cur_quan = cur_quan[0]  
                    new_quan = cur_quan - 1  

                    #update quantity field -subtract 1
                    cursor.execute("UPDATE gen_books SET quantity = %s WHERE book_id = %s", (new_quan, self.qr_data))
                    connection.commit()
                    print("Quantity updated successfully!")

                    if new_quan == 0:
                        cursor.execute("UPDATE gen_books SET availability = %s WHERE book_id = %s", ('not available', self.qr_data))
                        connection.commit()
                        print("Book not available")


                    #insert to database
                    insert_query = "INSERT INTO borrowed_books (book_id, borrower, date_borrowed, date_return, status) VALUES (%s,%s, %s, %s, %s)"
                    data_to_insert = (self.qr_data, self.qr_databorrowers, formatted_current_date, formatted_return_date, 'Borrowed')  # Define the values to be inserted
                    cursor.execute(insert_query, data_to_insert)
                    connection.commit()
                    print('Successfully inserted')

                cursor.close()
                connection.close()

        except Exception as e:
            print("Error fetching data from database:", str(e))

    def update(self):
        ret, frame = self.camera.read()
        if ret:
            decoded_objects = decode(frame)
            if decoded_objects:
                x, y, w, h = decoded_objects[0].rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                self.qr_detected = True
                self.qr_databorrowers = decoded_objects[0].data.decode('utf-8')
                self.qr_data = decoded_objects[0].data.decode('utf-8')
            else:
                self.qr_detected = False
                self.qr_databorrowers = ""
                self.qr_data = ""

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.photo = photo

        if self.capture_running:
            self.window.after(30, self.update)
        else:
            self.camera.release()

    def close_window(self):
        self.capture_running = False
        self.window.destroy()
        self.camera.release()

    def back_to_first_window(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the first window?")
        
        if asktoproceed:
            self.window.destroy()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.parent_window.deiconify()

class Return:
    def __init__(self, parent_window=None):
        self.parent_window = parent_window

        self.window = tk.Toplevel(parent_window)
        self.window.title("Return")

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 550)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

        self.canvas = tk.Canvas(self.window, width=640, height=480)
        self.canvas.pack()

        self.qr_detected = False
        self.qr_databorrowers = "" 
        self.qr_data = ""

        self.qr_borrower_label = Label(self.window, text="Borrower:")
        self.qr_borrower_label.pack()

        self.qr_data_label = Label(self.window, text="QR Code Data: ")
        self.qr_data_label.pack()

        self.borrower_button = Button(self.window, text="Scan Borrower", command=self.borrower_qr_code)
        self.borrower_button.pack()

        self.return_button = Button(self.window, text="Return", command=self.return_qr_code)
        self.return_button.pack()

        self.back_button = Button(self.window, text="Back to First Window", command=self.back_to_first_window)
        self.back_button.pack()

        self.capture_running = True
        self.update()

    def borrower_qr_code(self):
        if self.qr_detected:
            self.qr_borrower_label.config(text=f"Borrower: {self.qr_databorrowers}")

            self.return_button.config(state="active")
            self.borrower_button.config(state="disabled")

    def return_qr_code(self):
        if self.qr_detected:
            self.qr_data_label.config(text=f"QR Code Data: {self.qr_data}")
        
        try:
            with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='wonderpets', ssh_password='Bo0kLocator!',
            remote_bind_address=('wonderpets.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
                connection = MySQLdb.connect(
                    user='wonderpets',
                    passwd='chocolate290',
                    host='127.0.0.1', port=tunnel.local_bind_port,
                    db='wonderpets$db_library',
                )

                cursor = connection.cursor()

                #get quantity of the book_id detected
                cursor.execute("SELECT quantity FROM gen_books WHERE book_id = %s", (self.qr_data,))
                cur_quan = cursor.fetchone()

                if cur_quan:
                    cur_quan = cur_quan[0]  
                    new_quan = cur_quan + 1  

                    #update quantity field -subtract 1
                    cursor.execute("UPDATE gen_books SET quantity = %s WHERE book_id = %s", (new_quan, self.qr_data))
                    connection.commit()
                    print("Quantity updated successfully!")

                    if new_quan > 0:
                        cursor.execute("UPDATE gen_books SET availability = %s WHERE book_id = %s", ('available', self.qr_data))
                        connection.commit()
                        print("Book available")

                    #get date_return based from the macthed book_id and borrower detected
                    cursor.execute("SELECT date_return FROM borrowed_books WHERE book_id = %s and borrower = %s", (self.qr_data,self.qr_databorrowers))
                    cur_datereturn = cursor.fetchone()

                    if cur_datereturn:
                        cur_datereturn = cur_datereturn[0]

                        if current_date > cur_datereturn:
                            #update borrowed_books
                            cursor.execute("UPDATE borrowed_books SET status = %s WHERE book_id = %s and borrower = %s", ('Returned Late', self.qr_data, self.qr_databorrowers))
                            connection.commit()
                            print("returned late")
                        else:
                            cursor.execute("UPDATE borrowed_books SET status = %s WHERE book_id = %s and borrower = %s", ('Returned', self.qr_data, self.qr_databorrowers))
                            connection.commit()
                            print("returned")

                cursor.close()
                connection.close()

        except Exception as e:
            print("Error fetching data from database:", str(e))


    def update(self):
        ret, frame = self.camera.read()
        if ret:
            decoded_objects = decode(frame)
            if decoded_objects:
                x, y, w, h = decoded_objects[0].rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                self.qr_detected = True
                self.qr_data = decoded_objects[0].data.decode('utf-8')
                self.qr_databorrowers = decoded_objects[0].data.decode('utf-8')
            else:
                self.qr_detected = False
                self.qr_data = ""
                self.qr_databorrowers = ""

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.photo = photo

        if self.capture_running:
            self.window.after(30, self.update)
        else:
            self.camera.release()

    def close_window(self):
        self.capture_running = False
        self.window.destroy()
        self.camera.release()
    
    def back_to_first_window(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to the first window?")
        
        if asktoproceed:
            self.window.destroy()
            self.camera_running = False
            if self.camera.isOpened():
                self.camera.release()
            self.parent_window.deiconify()

class FirstWindow:
    def __init__(self, parent_window=None, scanuser=None):
        self.parent_window = parent_window
        self.window = tk.Toplevel(parent_window) 
        self.window.title("First Window")
        self.window.geometry("640x480")
        self.window.configure(bg="#ffffff")

        self.scanuser = scanuser
        self.scanuser_string = str(self.scanuser)  # Convert scanuser to string
        print(self.show_scanuser_label(self.scanuser_string))

        self.canvas = Canvas(
            self.window,
            bg="#ffffff",
            height=480,
            width=640,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "method.png")

        if os.path.exists(image_path):
            background_img = PhotoImage(file=image_path)
            label = Label(self.canvas, image=background_img, bd=0, highlightthickness=0)
            label.place(x=0, y=-25, relwidth=1, relheight=1)
            label.image = background_img  
        


        img0 = PhotoImage(file=os.path.join(script_dir, "img0.png"))
        self.b0 = Button(
            self.canvas,
            image=img0,
            borderwidth=2,
            highlightthickness=0,
            command=self.open_second_window,
            relief="flat"
        )
        self.b0.place(x=115, y=220, width=123, height=105)
        self.b0.image = img0  

        img1 = PhotoImage(file=os.path.join(script_dir, "img1.png"))
        self.b1 = Button(
            self.canvas,
            image=img1,
            borderwidth=2,
            highlightthickness=0,
            command=self.open_pers_window,
            relief="flat"
        )
        self.b1.place(x=258, y=220, width=123, height=105)
        self.b1.image = img1  

        img2 = PhotoImage(file=os.path.join(script_dir, "img2.png"))
        self.b2 = Button(
            self.canvas,
            image=img2,
            borderwidth=2,
            highlightthickness=0,
            command=self.open_third_window,
            relief="flat"
        )
        self.b2.place(x=400, y=220, width=123, height=105)
        self.b2.image= img2

        img3 = PhotoImage(file=os.path.join(script_dir, "img3.png"))
        self.b3 = Button(
            self.canvas,
            image=img3,
            borderwidth=0,
            highlightthickness=0,
            command=self.scan_user_window,
            relief="flat"
        )
        self.b3.place(x=258, y=350, width=123, height=25)
        self.b3.image= img3
    
    def show_scanuser_label(self, scanuser):
        label = Label(self.window, text=scanuser)
        label.pack()
        return scanuser

    def open_second_window(self):
        self.window.withdraw()
        scanuser_text = self.show_scanuser_label(self.scanuser_string)
        print("Scan User in First Window:", scanuser_text)
        main_app = MainApplication(self.window, scanuser_text)

    def open_pers_window(self):
        self.window.withdraw()
        Borrow(self.window)

    def open_third_window(self):
        self.window.withdraw()
        Return(self.window)

    def scan_user_window(self):
        asktoproceed = messagebox.askyesno("Confirmation", "Do you want to proceed to scan user again?")
        
        if asktoproceed:
            self.window.withdraw()
            user_window = tk.Toplevel(self.parent_window)
            user_window.title("User Window")
            User(user_window)