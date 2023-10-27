import sys
import os
import json
from datetime import datetime, date

import pytesseract
from passporteye import read_mrz
import face_recognition
import cv2

# Set the Tesseract OCR executable path.
pytesseract.pytesseract.tesseract_cmd = os.path.join(
    os.path.dirname(sys.path[0]), "Tesseract-OCR", "tesseract.exe"
)


def preprocess_image(image, image_path, output_folder):
    # Convert the image to grayscale.
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply noise reduction using Gaussian blur.
    blurred_image = cv2.GaussianBlur(gray_image, (3, 3), 0)

    # Increase sharpness using unsharp masking.
    sharpened_image = cv2.addWeighted(gray_image, 2, blurred_image, -1, 0)

    # Save the preprocessed image to the Output folder.
    preprocessed_image_path = os.path.join(output_folder, os.path.splitext(os.path.basename(image_path))[0] + "_preprocessed_image.jpg")
    cv2.imwrite(preprocessed_image_path, gray_image)

    return preprocessed_image_path


def find_issuing_date(image_path, extracted_fields, face_recognition_message):
    # Preprocess image for OCR with Tesseract.
    image = cv2.imread(image_path, 0)

    # Apply Otsu thresholding.
    _, thresh_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    # Perform OCR using Tesseract.
    extracted_text = pytesseract.image_to_string(thresh_image, lang='eng')

    # Find dates in format DD/MM/YYYY.
    import re

    date_pattern = r"\b(\d{2}/\d{2}/\d{4})\b"
    dates = re.findall(date_pattern, extracted_text)

    # Remove known dates (Expiry Date and Date of Birth).
    known_dates = [extracted_fields['expiry_date'], extracted_fields['date_of_birth']]
    dates = [date for date in dates if date not in known_dates]

    # # Print extracted text.
    # print("Extracted Text:")
    # print(extracted_text)

    # Print extracted dates.
    print("\nExtracted Date of Issue which is not in the MRZ:")
    if len(dates) != 0:
        for date in dates:
            print(date)
    else:
        print("No Issuing Date in DD/MM/YYYY format.")

    # Add extracted date of issue to fields.
    extracted_fields['date_of_issue'] = dates[0]

    # Update the formatted text.
    formatted_text = f"Name: {extracted_fields['name']}\n" \
                     f"Expiry Date: {extracted_fields['expiry_date']}\n" \
                     f"Date of Birth: {extracted_fields['date_of_birth']}\n" \
                     f"Date of Issue: {extracted_fields['date_of_issue']}\n" \
                     f"Passport Number: {extracted_fields['passport_number']}\n" \
                     f"Sex: {extracted_fields['sex']}\n" \
                     f"Nationality: {extracted_fields['nationality']}\n"
    formatted_text += face_recognition_message

    return extracted_fields, formatted_text


def extract_passport_portrait(input_path):
    # Create the Portraits folder in the Output folder if it doesn't exist.    
    portrait_output_folder = os.path.join(sys.path[0], "Output", "Portraits")
    os.makedirs(portrait_output_folder, exist_ok=True)

    # Load the input image.
    image = face_recognition.load_image_file(input_path)

    # Use face_recognition library for face detection.
    face_locations = face_recognition.face_locations(image)

    if len(face_locations) == 0:
        return "\nNo faces found in the image."

    # Assume the first detected face corresponds to the person's portrait.
    top, right, bottom, left = face_locations[0]

    # Calculate the new coordinates to increase the portrait area by 1.6 times.
    width = right - left
    height = bottom - top
    new_width = int(width * 1.4)
    new_height = int(height * 1.8)

    # Calculate the adjustment to keep the portrait centered.
    width_diff = new_width - width
    height_diff = new_height - height
    left -= width_diff // 2
    right += width_diff - width_diff // 2
    top -= height_diff // 2
    bottom += height_diff - height_diff // 2

    # Adjust the top and bottom coordinates to move the portrait higher by 0.15 of the height.
    height = bottom - top
    height_adjustment = int(height * 0.05)
    top -= height_adjustment
    bottom -= height_adjustment

    # Ensure the coordinates are within the image bounds.
    left = max(left, 0)
    right = min(right, image.shape[1])
    top = max(top, 0)
    bottom = min(bottom, image.shape[0])

    # Extract the person's portrait from the image.
    portrait = image[top:bottom, left:right]

    # Convert color space from BGR to RGB.
    portrait_rgb = cv2.cvtColor(portrait, cv2.COLOR_BGR2RGB)

    # Save the portrait image to the Output folder.
    output_path = os.path.join(portrait_output_folder, 
                               os.path.splitext(os.path.basename(input_path))[0] + "_portrait.jpg")
    cv2.imwrite(output_path, portrait_rgb)
    
    return "\nPortrait extracted and saved successfully."


def extract_fields(mrz_data):
    fields = {
        "name": "",
        "expiry_date": "",
        "date_of_birth": "",
        "date_of_issue": "",
        "passport_number": "",
        "nationality": "",
        "sex": ""
    }

    fields["name"] = mrz_data.get("names", "") + " " + mrz_data.get("surname", "")
    fields["name"] = fields["name"].replace("<", "")
    fields["expiry_date"] = mrz_data.get("expiration_date", "").replace("O", "0").replace("o", "0").replace("<", "")
    fields["date_of_birth"] = mrz_data.get("date_of_birth", "").replace("O", "0").replace("o", "0").replace("<", "")
    fields["passport_number"] = mrz_data.get("number", "").replace("O", "0").replace("o", "0").replace("<", "")
    fields["nationality"] = mrz_data.get("country", "").replace("<", "")
    fields["sex"] = mrz_data.get("sex", "").replace("<", "")

    # Convert expiry date to a common format (YYMMDD to DD/MM/YYYY).
    if len(fields["expiry_date"]) == 6:
        expiry_date = datetime.strptime(fields["expiry_date"], "%y%m%d").strftime("%d/%m/%Y")
        fields["expiry_date"] = expiry_date

    # Convert date of birth to a common format (YYMMDD to DD/MM/YYYY).
    if len(fields["date_of_birth"]) == 6:
        dob = datetime.strptime(fields["date_of_birth"], "%y%m%d").strftime("%d/%m/%Y")
        fields["date_of_birth"] = dob

    # Adjust century if the birth date is in the future.
    if datetime.strptime(dob, "%d/%m/%Y").date() > date.today():
        dob = dob[:-4] + str(int(dob[-4:]) - 100)
        fields["date_of_birth"] = dob

    formatted_text = f"Name: {fields['name']}\n" \
                     f"Expiry Date: {fields['expiry_date']}\n" \
                     f"Date of Birth: {fields['date_of_birth']}\n" \
                     f"Passport Number: {fields['passport_number']}\n" \
                     f"Sex: {fields['sex']}\n" \
                     f"Nationality: {fields['nationality']}\n"

    return fields, formatted_text


def ocr_passport(image_path):
    output_folder = os.path.join(sys.path[0], "Output")
    os.makedirs(output_folder, exist_ok=True)
    
    json_output_folder = os.path.join(output_folder, "JSON_Files")
    os.makedirs(json_output_folder, exist_ok=True)

    face_recognition_message = extract_passport_portrait(image_path)
    
    # Preprocess image and get the path of the preprocessed image.
    preprocessed_image_path = preprocess_image(cv2.imread(image_path), image_path, output_folder)
    
    # Process preprocessed image using passporteye.
    mrz = read_mrz(preprocessed_image_path)

    # Obtain MRZ data.
    mrz_data = mrz.to_dict()

    extracted_fields, formatted_text = extract_fields(mrz_data)
    formatted_text += face_recognition_message
    
    try:
        extracted_fields, formatted_text = find_issuing_date(image_path, extracted_fields, face_recognition_message)
    except IndexError:
        # No issuing date in DD/MM/YYYY format.
        pass

    output_file = os.path.join(json_output_folder, os.path.splitext(os.path.basename(image_path))[0] + ".json")

    with open(output_file, "w") as file:
        json.dump(extracted_fields, file, indent=4)
    
    return extracted_fields, formatted_text


if __name__ == "__main__":
    image_path = input("Enter the path to the passport photo: ")

    extracted_fields, formatted_text = ocr_passport(image_path)
    print(f"\n{json.dumps(extracted_fields, indent=4)}")
    
    print(f"\n{formatted_text}")
