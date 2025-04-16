import os
import re
import PyPDF2

# === Setup ===
pdf_path = input('Please enter file path to pdf:')
output_folder = "complete"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

KEYWORD_SUFFIXES = {
    "Dear Dr": "GP_Letters",
    "Dear Doctor": "GP_Letters"
}

# === Extract client number ===
def extract_client_number(text):
    match = re.search(r"Ref No:\s*(\d{6})", text)
    return match.group(1) if match else None

# === Extract date (DDMMYYYY format) ===
def extract_date(text):
    match = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", text)
    if match:
        day, month, year = match.groups()
        month_number = {
            "January": "01", "February": "02", "March": "03", "April": "04",
            "May": "05", "June": "06", "July": "07", "August": "08",
            "September": "09", "October": "10", "November": "11", "December": "12"
        }
        return f"{day.zfill(2)}{month_number.get(month, '00')}{year}"
    return None

# === Determine file suffix based on content
def determine_file_suffix(text):
    for phrase, suffix in KEYWORD_SUFFIXES.items():
        if phrase.lower() in text.lower():
            return suffix
    return "Participant Files"  # default fallback

# === Main PDF Split Logic ===
with open(pdf_path, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    writer = None
    current_client = None
    current_date = None
    group_text = ""  # NEW: collect text for full client section

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        group_text += text + "\n"  # NEW: build up full section text

        # Try to extract new client or date
        client_number = extract_client_number(text)
        date = extract_date(text)

        if client_number and client_number != current_client:
            # Save previous group
            if writer and current_client:
                file_suffix = determine_file_suffix(group_text)  # ✅ use full group text
                base_name = f"{current_client}_{file_suffix}.pdf"
                if current_date:
                    base_name = f"{current_client}_{current_date}_{file_suffix}.pdf"

                new_path = os.path.join(output_folder, base_name)

                # Avoid overwrite
                counter = 1
                while os.path.exists(new_path):
                    if current_date:
                        new_path = os.path.join(output_folder, f"{current_client}_{current_date}_{file_suffix}_{counter}.pdf")
                    else:
                        new_path = os.path.join(output_folder, f"{current_client}_{file_suffix}_{counter}.pdf")
                    counter += 1

                with open(new_path, "wb") as out_file:
                    writer.write(out_file)
                print(f"Saved: {os.path.basename(new_path)}")

            # Start new writer and reset tracking
            writer = PyPDF2.PdfWriter()
            current_client = client_number
            current_date = date
            group_text = text + "\n"  # ✅ reset and start new group text
        elif date and not current_date:
            current_date = date  # Keep date if it comes later in section

        # Add current page to the current writer
        if writer:
            writer.add_page(page)

    # Save the final client file
    if writer and current_client:
        file_suffix = determine_file_suffix(group_text)  # ✅ final group
        base_name = f"{current_client}_{file_suffix}.pdf"
        if current_date:
            base_name = f"{current_client}_{current_date}_{file_suffix}.pdf"

        new_path = os.path.join(output_folder, base_name)

        # Ensure unique filename
        counter = 1
        while os.path.exists(new_path):
            if current_date:
                new_path = os.path.join(output_folder, f"{current_client}_{current_date}_{file_suffix}_{counter}.pdf")
            else:
                new_path = os.path.join(output_folder, f"{current_client}_{file_suffix}_{counter}.pdf")
            counter += 1

        with open(new_path, "wb") as out_file:
            writer.write(out_file)
        print(f"Saved: {os.path.basename(new_path)}")
