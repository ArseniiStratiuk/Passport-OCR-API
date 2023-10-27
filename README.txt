OCR Your Passport


This project is a graphical user interface (GUI) application that performs 
Optical Character Recognition (OCR) on passport photos. It extracts relevant 
information from the Machine Readable Zone (MRZ) of the passport, such as 
the passport holder's name, passport number, nationality, sex, date of birth, 
date of issue, and expiry date. Additionally, it uses face recognition to 
extract and save the portrait from the passport photo.


Instructions:
1. Prerequisites:
   - Python 3.x installed on your system.
   - You also need to complete the instructions on this webpage https://github.com/ageitgey/face_recognition/issues/175#issue-257710508, 
     they are needed for face_recognition library. Here are these instructions:

     Requirments:
     (I've used this tutorial with these tools installed on Windows 10, but the newer versions may work too.)

     Microsoft Visual Studio 2015 (or newer) with C/C++ Compiler installed. (Visual C++ 2015 Build Tools didn't 
     work for me, and I got into problems in compiling dlib);
     Of course Python3 (I used Python3.5 x64 but the other versions may work too);
     CMake for windows and add it to your system environment variables.

   - The required Python packages can be installed using the following command:
     ```
     pip install pillow pytesseract passporteye dlib face_recognition opencv-python customtkinter regex
     ```
   - Tesseract OCR engine does not have to be installed on your system. It is 
     built in the project. You can find its files in the Tesseract-OCR folder.

2. Run the application:
   - Open a terminal or command prompt.
   - Navigate to the project directory.
   - Run the following command to start the application:
     ```
     python GUI.py
     ```
   - The GUI window will open, displaying the "OCR Your Passport" application.

3. Using the application:
   - Click on the "Select a Passport Photo" button.
   - Choose a passport photo image file (.jpg or .png) from your local system.
   - The application will perform OCR on the passport photo and display the extracted MRZ text in the textbox.
   - If the MRZ text is successfully extracted, the passport photo will be displayed in the frame on the left, 
     and the extracted fields will be shown in the textbox.
   - If the MRZ text cannot be extracted or an error occurs, an error message will be displayed in the textbox.
   - The application also extracts and saves the person's portrait from the passport photo, which can be found 
     in the "Output/Portraits" folder.

4. Changing the Window Appearance:
   - The application supports two appearance modes: "Dark" and "Light".
   - To change the window appearance, use the "Window Appearance" option menu at the bottom of the window.
   - Select either "Dark" or "Light" to switch to the desired appearance mode.

Note: This application uses the Tesseract OCR engine for text extraction and the face_recognition library for 
      face detection. Make sure you have the necessary dependencies installed and configured properly.

For additional instructions on how to use the program please check out the video Passport-OCR.mp4.