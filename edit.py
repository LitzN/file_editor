import os
import re
import PyPDF2

# Folder containing PDFs
pdf_folder = "./"

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = " ".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()

# Function to extract client number using regex
def extract_client_number(text):
    match = re.search(r"Reg No:\s*(\d{6})\s*", text)  # Example: Looking for "Reg No: 088889"
    return match.group(1) if match else None

    # Extract date in DDMMYYYY format
def extract_date(text):
    match = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", text)
    if match:
        day, month, year = match.groups()
        month_number = {
            "January": "01", "February": "02", "March": "03", "April": "04",
            "May": "05", "June": "06", "July": "07", "August": "08",
            "September": "09", "October": "10", "November": "11", "December": "12"
        }
        return f"{day.zfill(2)}{month_number.get(month, '00')}{year}"  # Converts "05 August 2009" → "05082009"
    return None


# Process all PDFs in the folder
for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        extracted_text = extract_text_from_pdf(pdf_path)
        
        client_number = extract_client_number(extracted_text)
        date = extract_date(extracted_text)
        if client_number:
            new_filename = f"{client_number}_Participant Files.pdf"
            if date:
                new_filename = f"{client_number}_{date}_Participant Files.pdf"
            new_path = os.path.join(pdf_folder, new_filename)

            # Ensure unique filenames
            counter = 1
            while os.path.exists(new_path):
                new_path = os.path.join(pdf_folder, f"{client_number}_{date}_{counter}.pdf")
                counter += 1

            os.rename(pdf_path, new_path)
            print(f"Renamed: {filename} → {os.path.basename(new_path)}")
        else:
            print(f"No client number found in {filename}, skipping.")