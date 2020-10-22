import face_recognition
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk,Image
from tkinter.filedialog import askopenfilename
import numpy as np
import cv2
from gtts import gTTS
import mysql.connector
import os
import sys
from io import BytesIO
from datetime import datetime


MyDB = mysql.connector.connect(
    host = "localhost", #xampp must be open and start Apache and mysql
    user = "root",
    password = "",
    database = "People" #Data base name in phpMyAdmin must be named "People"
)

#Function to insert Unknown with photo
def insertUnknown(binData):
    SQLStatment2 = "INSERT INTO Unknown (photo) VALUES (%s)"
    MyCursor1.execute(SQLStatment2,(binData,))
    MyDB.commit()

#Function to insert Known with name and photo
def insertKnownFromCamera(binData):
    name = known_name.get()
    SQLStatment1 = "INSERT INTO Known (name,photo) VALUES (%s,%s)"
    MyCursor2.execute(SQLStatment1,(name,binData,))
    MyDB.commit()

def insertKnownFromUpload():
    unknown_image = face_recognition.load_image_file(filename)
    found = False
    X = countKnown()
    SQLStatment1 = "SELECT* FROM Known"
    MyCursor2.execute(SQLStatment1)
    for x in range(X):
        record = MyCursor2.fetchone()
        name = record[1]
        blob_image = record[2]
        file_like = BytesIO(blob_image)
        img2 = Image.open(file_like)
        known_image = face_recognition.load_image_file(file_like)
        #img2.show()
        try:
            known_encoding = face_recognition.face_encodings(known_image)[0]
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        except IndexError as e:
            print(e)
            break
        results = face_recognition.compare_faces([known_encoding], unknown_encoding,tolerance=0.55)
        if(results[0]):
            found = True
            messagebox.showinfo("", "This person already exist as: "+name)
            #print("This person already exist as: "+name)
            break

    if(found == False):
        imName = pname.get()
        insertKnownFromFile(imName,filename)
        messagebox.showinfo("", "Inserted successfully!")
        #print("Inserted successfully!")

def insertKnownFromFile(name, FilePath):
    with open(FilePath,"rb") as File:
        BinaryData = File.read()
    SQLStatment1 = "INSERT INTO Known (name,photo) VALUES (%s,%s)"
    MyCursor2.execute(SQLStatment1,(name,BinaryData,))
    MyDB.commit()

#return the number of Known in the DB
def countUnknown():
    SQLStatment4 = "SELECT count(id) from Unknown"
    MyCursor1.execute(SQLStatment4)
    Y = MyCursor1.fetchone()[0]
    return Y

#return the number of Known in the DB
def countKnown():
    SQLStatment3 = "SELECT count(id) from Known"
    MyCursor2.execute(SQLStatment3)
    X = MyCursor2.fetchone()[0]
    return X

def getDate_time():
    # datetime object containing current date and time
    now = datetime.now()
    #print("now =", now)
    # dd/mm/YY H:M:S
    dt_string = now.strftime("_%d-%m-%Y_%H-%M-%S")
    #print("date and time =", dt_string)
    return dt_string

filename = ""
def filedialog():
    global filename
    filename = askopenfilename(title="Select A File", filetype=(("jpg files", "*.jpg"), ("all files", "*.*")))
    label = Label(up, text=" browse")
    label.grid(column=1, row=2)
    label.configure(text=filename)

    img = Image.open(filename)
    img = img.resize((350, 350))
    photo = ImageTk.PhotoImage(img)
    label2 = Label(image=photo)
    label2.image = photo
    label2.place(x=150, y=100)

intro = Tk()
choice = 0
def uploadPhoto():
    print("uplooooad!")
    global choice
    choice = 1
    global intro
    intro.destroy()

def openCamera():
    print("opeeeeen!")
    global choice
    choice = 2
    global intro
    intro.destroy()

intro.title("Hackathon 2020")
intro.iconbitmap(r'Media/icons/jesics.ico')
intro.geometry("400x300")

image1 = PhotoImage(file='Media/icons/uploadphoto.png')
uploadimg = image1.subsample(2, 2)
#UploadPhoto = Button(intro, text="Upload photo", padx=30, image=uploadPhoto, compound=RIGHT, width=90, height=48, command=lambda:[uploadPhoto()""", intro.destroy()"""]).place(x=40, y=100)
Uploadimg = Button(intro, text="Upload photo", padx=30, image=uploadimg, compound=RIGHT, width=90, height=48, command=uploadPhoto).place(x=40, y=100)
image2 = PhotoImage(file='Media/icons/camera.png')
openCam = image2.subsample(2, 2)
#OpenCam = Button(intro, text="Open Camera", padx=30,  image=camera, compound=RIGHT, width=90, height=48, command=lambda:[openCamera()""", intro.destroy()"""]).place(x=220, y=100)
OpenCam = Button(intro, text="Open Camera", padx=30,  image=openCam, compound=RIGHT, width=90, height=48, command=openCamera).place(x=220, y=100)
intro.mainloop()


if choice == 1: ######################### UPLOAD IMAGE #########################
    MyCursor2 = MyDB.cursor(buffered = True) #DataBase object
    MyCursor2.execute("CREATE TABLE if not exists Known (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, name VARCHAR(45), photo LONGBLOB NOT NULL)")
    #imPath = "Muhannad.jpeg"
    #imPath = "Kamel.jpg"

    ##########################
    up = Tk()

    up.title("Upload to Add Form")
    up.iconbitmap(r'Media/icons/jesics.ico')
    up.geometry("600x600")

    label = Label(up, text='Name :  ').place(x=130, y=470)
    pname = StringVar(up)
    Name = Entry(up, textvariable = pname, width=40).place(x=180, y=470)

    image1 = PhotoImage(file='Media/icons/browse.png')
    upload = image1.subsample(2, 2)
    Browse = Button(up, text="Browse", padx=30, image=upload, compound=RIGHT, width=90, height=48, command=filedialog).place(x=220, y=20)

    image3 = PhotoImage(file='Media/icons/save.png')
    save = image3.subsample(1, 1)
    Save = Button(up, text="Save", padx=30, image=save, compound=RIGHT, width=90, height=48, command=lambda:[insertKnownFromUpload(), up.destroy()]).place(x=220, y=510)

    up.mainloop()

elif choice == 2: ######################### OPEN CAMERA #########################
    MyCursor1 = MyDB.cursor(buffered = True) #DataBase object
    MyCursor2 = MyDB.cursor(buffered = True) #DataBase object

    MyCursor1.execute("CREATE TABLE if not exists Unknown (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, photo LONGBLOB NOT NULL)")
    MyCursor2.execute("CREATE TABLE if not exists Known (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, name VARCHAR(45), photo LONGBLOB NOT NULL)")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) #0 for laptop camera, 1 for another camera

    date_and_time = getDate_time()

    while (True):
        ret, frame = cap.read()
        ret2, frame2 = cap.read()
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]
        # Find all the faces in the current frame of video
        face_locations = face_recognition.face_locations(rgb_frame)
        #Display the results
        for top, right, bottom, left in face_locations:
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        # Display the resulting image
        window_name = "Video"
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1)
        if key == 27: # exit on ESC
            cv2.imwrite("Media/persons"+date_and_time+".jpg",frame2)
            break

    cap.release()
    cv2.destroyAllWindows()

    # Detecting the faces
    image = face_recognition.load_image_file("Media/persons"+date_and_time+".jpg")  # Load the image
    face_locations = face_recognition.face_locations(image)  # Detect the face locations

    faces_num = len(face_locations)

    print(faces_num)

    for i in range(faces_num):
        # Convert the face_recognition image to a PIL image
        img = Image.fromarray(image, 'RGB')

        # Creating the image with red box
        img_with_red_box = img.copy()  # Create a copy of the original image so there is not red box in the cropped image later

        #Creating the cropped image
        img_cropped = img.crop((  # Crop the original image
            face_locations[i][3],
            face_locations[i][0],
            face_locations[i][1],
            face_locations[i][2]
        ))

        stream = BytesIO()
        img_cropped.save(stream, format="JPEG")
        BinaryData = stream.getvalue()
        insertUnknown(BinaryData)

    persons = []
    un_persons = dict()
    Y = countUnknown()
    SQLStatment5 = "SELECT* FROM Unknown"
    MyCursor1.execute(SQLStatment5)
    for y in range(Y):
        record1 = MyCursor1.fetchone()
        blob_image1 = record1[1]
        file_like1 = BytesIO(blob_image1)
        img1 = Image.open(file_like1)
        unknown_image = face_recognition.load_image_file(file_like1)
        #img1.show()
        found = False
        X = countKnown()
        SQLStatment6 = "SELECT* FROM Known"
        MyCursor2.execute(SQLStatment6)
        for x in range(X):
            record2 = MyCursor2.fetchone()
            name = record2[1]
            blob_image2 = record2[2]
            file_like2 = BytesIO(blob_image2)
            img2 = Image.open(file_like2)
            known_image = face_recognition.load_image_file(file_like2)
            #img2.show()
            try:
                known_encoding = face_recognition.face_encodings(known_image)[0]
                unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            except IndexError as e:
                print(e)
                break
            results = face_recognition.compare_faces([known_encoding], unknown_encoding,tolerance=0.55)
            if(results[0]):
                found = True
                persons.append(name)
                break

        if(found == False):
            un_persons[y] = -1; #saving which face is a stranger to ask about it later


    print(persons)
    print(un_persons)

    myText = ""
    for per in range(len(persons)):
        myText += persons[per]
        if((per + 1) < len(persons)):
            myText += " and"

    if(len(persons) > 0):
        if(len(un_persons) == 1):
            myText += " and a stranger"
        elif(len(un_persons) > 1):
            myText += " and " + str(len(un_persons)) + " strangers"
    else:
        if(len(un_persons) == 1):
            myText += "A stranger"
        elif(len(un_persons) > 1):
            myText += str(len(un_persons)) + " strangers"

    if(len(persons) > 0 or len(un_persons) > 0):
        language = 'en'
        myText += " at the door!"
        myobj = gTTS(text=myText, lang=language, slow=False)
        myobj.save("Media/voice"+date_and_time+".mp3")
        os.system("start Media/voice"+date_and_time+".mp3")


    SQLStatment7 = "SELECT* FROM Unknown"
    MyCursor1.execute(SQLStatment7)
    j = 0
    for k in un_persons:
        #unknown_image = face_recognition.load_image_file("unknown/face"+str(u)+".jpg")
        record1 = MyCursor1.fetchone()
        if(k != record1[0] - 1):
            continue
        blob_image1 = record1[1]
        file_like1 = BytesIO(blob_image1)
        img1 = Image.open(file_like1)
        j += 1
        root = Tk()
        root.title(str(j)+"- Who is this person?")
        root.iconbitmap(r'Media/icons/jesics.ico')
        root.geometry("300x300")
        label = Label(root, text='Name :  ').place(x=40, y=30)
        known_name = StringVar(root)
        Name = Entry(root, textvariable = known_name, width=30).place(x=90, y=30)

        #canvas = Canvas(root, width = 200, height = 200, bg = "white")
        canvas = Canvas(root, width = 200, height = 200)
        canvas.pack(pady=90)
        unknown_img = ImageTk.PhotoImage(img1)
        canvas.create_image(100, 100, anchor=CENTER, image=unknown_img)

        image1 = PhotoImage(file='Media/icons/save.png')
        save = image1.subsample(2, 2)
        Save = Button(root, text="Save", padx=30, image=save, compound=RIGHT, width=20, height=25, command=lambda:[insertKnownFromCamera(blob_image1), root.destroy()]).place(x=20, y=250)

        image2 = PhotoImage(file='Media/icons/close.png')
        closeWithoutSave = image2.subsample(2, 2)
        CloseWithoutSave = Button(root, text="Don't save and Close", padx=20,image = closeWithoutSave, compound=RIGHT, width=120, height=25, command=root.destroy).place(x=110, y=250)


        root.mainloop()

    SQLStatment8 = "DROP TABLE Unknown"
    MyCursor1.execute(SQLStatment8)
