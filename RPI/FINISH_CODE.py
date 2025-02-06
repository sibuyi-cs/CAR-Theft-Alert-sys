import RPi.GPIO as GPIO
import time
from rpi_lcd import LCD
import cv2
from datetime import datetime
import time
import dropbox
from twilio.rest import Client

row1 = 6
row2 = 13
row3 = 19
row4 = 26

col1 = 12
col2 = 16
col3 = 20
col4 = 21


entered_passcode=""
correct_passcode=""

MAX_FAILED_ATTEMPTS = 3
failed_attempts = 0

stop_prompting = True
password = False


global ARM_
ARM_=False
lcd=LCD()


# Dropbox access token
access_token = 'sl.CCT5dQO6PmtU44rW7n_GXVbAO5FOq5iIRmFdOLuMmKymMYihzavJ5SX0'

dbx = dropbox.Dropbox(access_token)

# Twilio credentials
account_sid = 'AC8dfef39c1e5fdbc309b5ea120e'
auth_token = 'fb9b6720a868ebc849c2f4'

twilio_number = "+12562429435"  # Your Twilio phone number
recipient_number = "+27712427659"  # Recipient's phone number
# recipient_number = "whatsapp:+27712427659"  # Recipient's phone number
# twilio_number = "whatsapp:+14155238886"  # Your Twilio phone number

def take_pictures_and_upload():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not access the camera.")
        exit()

    num_pictures = 5  # Number of pictures to take
    delay = 2  # Delay in seconds between each picture
    filenames = []  # Array to store filenames

    for i in range(num_pictures):
        # Capture a frame
        ret, frame = camera.read()
        if not ret:
            print("Error: Failed to capture image.")
            break
        # Generate a timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"sys_image_{timestamp}.jpg"
        filenames.append(filename)  # Store the filename in the array

        # Save the frame to the file
        cv2.imwrite(filename, frame)
        print(f"Picture {i + 1} saved as {filename}")

        cv2.waitKey(500)  # Show the frame for 500ms
        time.sleep(delay)

    # Upload the captured images to Dropbox and generate shareable links
    shareable_links = upload_to_dropbox_and_get_links(filenames)

    # Send the links via Twilio
    send_links_via_twilio(shareable_links)

    print("All pictures taken, uploaded, and links sent. Exiting...")
    camera.release()


def upload_to_dropbox_and_get_links(filenames):
    shareable_links = []
    for filename in filenames:
        try:
            # Upload the file to Dropbox
            with open(filename, "rb") as f:
                dropbox_path = f"/{filename}"  # Path in Dropbox
                dbx.files_upload(f.read(), dropbox_path, mute=True)
                print(f"Uploaded {filename} to Dropbox at {dropbox_path}")

            # Create a shareable link
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
            shareable_links.append(shared_link_metadata.url)
        except Exception as e:
            print(f"Error uploading {filename} or creating a shareable link: {e}")
    return shareable_links

def send_links_via_twilio(links):
    # Create a Twilio client
    client = Client(account_sid, auth_token)
    try:
        # Combine all links into a single message
        message_body = "Images from system:\n" + "\n".join(links)

        # Send the message
        message = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=recipient_number
            )
        print(f"Message sent! SID: {message.sid}")
    except Exception as e:
        print(f"Error sending message via Twilio: {e}")

# Call the function to take pictures, upload them to Dropbox, and send links via Twilio

def buttons_init():
    # START STOP ARM SYSTEM setup
    global start
    global stop_
    global arm_s
    global device_armed_pin
    global send_image_pin

    start=11
    stop_=10
    arm_s=9

    start_HIGH=25
    stop_HIGH=8
    arms_HIGH=7

    device_armed_pin=22
    send_image_pin=27


    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    # SET PINS AS INPUT pulled down

    GPIO.setup(start, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(stop_, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(arm_s, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(send_image_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    #SET PINS AS OUTPUT
    GPIO.setup(start_HIGH,GPIO.OUT)
    GPIO.setup(stop_HIGH, GPIO.OUT)
    GPIO.setup(arms_HIGH, GPIO.OUT)
    GPIO.setup(device_armed_pin, GPIO.OUT)

    #SET PINS HIGH
    GPIO.output(start_HIGH,GPIO.HIGH)
    GPIO.output(stop_HIGH, GPIO.HIGH)
    GPIO.output(arms_HIGH, GPIO.HIGH)
    #END FUNCTION

def keypad_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(col1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(col2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(col3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(col4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(row1, GPIO.OUT)
    GPIO.setup(row2, GPIO.OUT)
    GPIO.setup(row3, GPIO.OUT)
    GPIO.setup(row4, GPIO.OUT)
    #END FUNCTION

def readLine(line, characters):
    global entered_passcode
    keypad_init()

    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(col1) == 1):
        entered_passcode += characters[0]
        if characters[0] == "*" and len(entered_passcode) > 0:
            entered_passcode = entered_passcode[:-2]
        print(entered_passcode)
        lcd.text("PASSCODE:"+entered_passcode,1)
        lcd.text(" ",2)

    elif(GPIO.input(col2) == 1):
        entered_passcode += characters[1]
        if characters[1] == "*" and len(entered_passcode) > 0:
            entered_passcode = entered_passcode[:-2]
        print(entered_passcode)
        lcd.text("PASSCODE:"+entered_passcode,1)
        lcd.text(" ",2)

    elif(GPIO.input(col3) == 1):
        entered_passcode += characters[2]
        if characters[2] == "*" and len(entered_passcode) > 0:
            entered_passcode = entered_passcode[:-2]
        print(entered_passcode)
        lcd.text("PASSCODE:"+entered_passcode,1)
        lcd.text(" ",2)

    elif(GPIO.input(col4) == 1):
        entered_passcode += characters[3]
        if characters[3] == "*" and len(entered_passcode) > 0:
            entered_passcode = entered_passcode[:-2]
        print(entered_passcode)
        lcd.text("PASSCODE:"+entered_passcode,1)
        lcd.text(" ",2)
    GPIO.output(line, GPIO.LOW)
    #END FUCNTION

def correct_passcode_entered():
    global entered_passcode
    global stop_prompting
    global password

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(15, GPIO.OUT) # GREEN LED
    print("Passcode accepted. Access granted.")
    GPIO.output(15, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(15, GPIO.LOW)
    entered_passcode = ""
    stop_prompting = False
    password=True
    GPIO.cleanup()

def incorrect_passcode_entered():
    global entered_passcode
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT) # RED LED
    print("Incorrect passcode. ")
    lcd.text("INCORRECT!",1)
    time.sleep(2)
    lcd.text("Try Again!",2)
    time.sleep(2)
    lcd.text(" ",2)
    GPIO.output(18, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(18, GPIO.LOW)
    entered_passcode = ""
    GPIO.cleanup()
    print("ENTER YOUR PASSWORD")
    lcd.text("Enter code",1)

def scankeys():
    global entered_passcode
    global correct_passcode
    global stop_prompting
    global failed_attempts

    GPIO.setmode(GPIO.BCM)
    while stop_prompting:
        readLine(row1, ["1", "2", "3", "A"])
        readLine(row2, ["4", "5", "6", "B"])
        readLine(row3, ["7", "8", "9", "C"])
        readLine(row4, ["*", "0", "#", "D"])
        time.sleep(0.2)
        if len(entered_passcode) == len(correct_passcode):
            if entered_passcode == correct_passcode:
                correct_passcode_entered()
                failed_attempts = 0
                time.sleep(2)
                lcd.text("Correct Code",1)
                time.sleep(2)
                lcd.text("ARM THE DEVICE",2)
            else:
                incorrect_passcode_entered()
                failed_attempts += 1
                if failed_attempts >= MAX_FAILED_ATTEMPTS:
                    print("SYSTEM ON LOCKDOWN")
                    lcd.clear()
                    lcd.text("  Failed Auth ...",1)
                    lcd.text("  System Locked ...",2)

                    time.sleep(2)
                    lcd.text(" Alarm Activated",1)

def sys_start_init():
    lcd.clear()
    lcd.text("WELCOME TO",1)
    time.sleep(2)
    lcd.text("Car Alert sys",2)
    time.sleep(3)

buttons_init()
keypad_init()
sys_start_init()
try:

    while True:

        if (GPIO.input(start)==1):
            print("START PRESSED")
            time.sleep(1)

            while password==False:
                stop_prompting = True
                lcd.text("Enter System",1)
                lcd.text("Code",2)
                print("ENTER YOUR PASSWORD:")
                correct_passcode = "7896AB"
                scankeys()
                stop_prompting = True


            buttons_init()
            while(GPIO.input(arm_s)==0):
                pass
            if (GPIO.input(arm_s)==1 and password==True  or ARM_==True):
                ARM_=True
                buttons_init()
                GPIO.output(device_armed_pin, GPIO.HIGH)
                print("arm_s PRESSED")
                lcd.text("DEVICE ARMED",1)
                lcd.text(" ",2)
                time.sleep(5)

 
                while (GPIO.input(stop_)==0):
                    print("ARMED")
                    lcd.text("ARMED",1)
                    lcd.text("Detecting!!!",2)

                    if GPIO.input(send_image_pin)==1:
                        print("sending a picture")
                        take_pictures_and_upload()
                        lcd.text("OBJECT IN PROX",1)
                        lcd.text(" ",2)
                        time.sleep(2)
                        lcd.text("SENDING IMAGE!",2)
                        time.sleep(1)

            while(GPIO.input(stop_)==0):
                pass
            if (GPIO.input(stop_)==1):
                buttons_init()
                GPIO.output(device_armed_pin, GPIO.LOW)
                print("STOPPED")
                lcd.text("DEVICE",1)
                lcd.text("DISARMED",2)
                ARM_=False
                time.sleep(1)

            password = False



except KeyboardInterrupt:
    print("\nApplication stopped!")

finally:
    GPIO.cleanup()
