# README

## Overview

This README provides details about the assumptions, trade-offs, design decisions, and simplifications made in the development of our email-based report processing system. The system is designed to poll unread emails from a server, extract patient details from attached reports, summarize the information, and send it to the corresponding doctor.

## Assumptions

1. **Unread Emails Only**: The system will poll only for unread messages from the server. This ensures that we process only new reports and avoid reprocessing old ones.
   
2. **Report in Attachment**: We assume that the medical report is always in the email attachment and not in the body of the email. This simplifies the extraction process.

3. **Doctor Name Variations**: The name of the doctor on the report may have initials or minor mismatches. The system is designed to handle these gracefully, ensuring accurate identification.

4. **Doctor Database**: We assume that the doctor exists in our database, allowing for straightforward matching and notification.

5. **Email Protocols**: We assume the use of IMAP for fetching emails and SMTP for sending emails, as these are standard protocols for email communication.

## Trade-offs and Design Decisions

1. **Document Parsing with LlamaParse**:
   - **Choice**: We chose [LlamaParse](https://www.llamaparse.com) for its ability to handle complex PDFs with tables and charts, which are common in medical reports.
   - **Integration**: LlamaParse integrates with LlamaIndex, enhancing retrieval and context augmentation.
   - **Alternatives Considered**: Other tools like PDFMiner.six, PyPDF, and OCR tools (e.g., Pytesseract) were considered. However, these tools either lack the ability to handle complex document structures or require more resources for comprehensive parsing.
   - **Trade-off**: While LlamaParse is powerful, it may be more resource-intensive than simpler parsing tools. However, its integration with LlamaIndex and support for multiple file types make it suitable for our needs.

2. **Feature Extraction with OpenAI GPT-4**:
   - **Choice**: We use the OpenAI GPT-4 model for extracting features such as doctor and patient names and for summarizing reports.
   - **Trade-off**: GPT-4 is cutting-edge but can be costly. In the future, we may consider using a custom-trained model like [BERT](https://en.wikipedia.org/wiki/BERT_(language_model)) for named entity recognition to reduce costs.

   ### Zero-Shot Prompting
   - **Choice**: We employ zero-shot prompting for feature extraction, which simplifies the implementation by not requiring example data. More information on zero-shot prompting can be found [here](https://www.promptingguide.ai/techniques/zeroshot).
   - **Zero-Shot Prompt Example**: "Extract the doctor and patient names from the attached report and provide a summary."
   - **Trade-off**: While zero-shot prompting is efficient, using more structured prompts or an agent framework could improve accuracy and scalability in production.

   ### Doctor Name Normalization
   - **Choice**: We use OpenAI queries to match extracted doctor names to those in our database, leveraging the small size of the doctor list.
   - **Trade-off**: For larger lists, we might need to implement a fuzzy search using tools like Elasticsearch to improve performance.

3. **Architecture**:
   - **Choice**: Email polling and processing are handled in the same loop for simplicity.
   - **Trade-off**: This approach may not scale well with increased load. Separating these tasks and processing emails concurrently across workers could enhance scalability.

## Simplifications and Shortcuts

1. **In-Memory Data Store**:
   - **Reasoning**: For this proof of concept (POC), we use an in-memory store instead of an external datastore. This decision was made to simplify the setup and focus on demonstrating core functionality.

2. **Single OpenAI Query**:
   - **Reasoning**: We opted for a single OpenAI query without examples to reduce complexity and expedite development. In a production environment, more sophisticated prompting strategies could be employed.

3. **No External Datastore**:
   - **Reasoning**: To keep the POC lightweight and easy to deploy, we did not integrate an external datastore. This can be reconsidered for a full-scale implementation.

By documenting these assumptions, trade-offs, and simplifications, we provide a clear understanding of the current system's capabilities and limitations, paving the way for future enhancements and scalability improvements.

## Usage

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set up a virtual environment (optional but recommended):**

   ```bash
   python -m venv .venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables

Before running the application, you need to set the following environment variables:

- `LAMA_PARSE_API_KEY`: Your LAMA Parse API key.
- `OPEN_API_KEY`: Your Open API key.
- `EMAIL_USER`: Your email username.
- `EMAIL_PASSWORD`: Your email password.

You can set these environment variables in your shell or create a `.env` file in the project root with the following format:

```plaintext
LAMA_PARSE_API_KEY=your_lama_parse_api_key
OPEN_API_KEY=your_open_api_key
EMAIL_USER=receptionist_email_user
EMAIL_PASSWORD=receptionist_email_password
```

### Usage

Run the application using the following command:

```bash
python main.py --imap_endpoint "imap.gmail.com" --smtp_endpoint "smtp.gmail.com" --smtp_port 587 --from_email_filter "someemail@gmail.com"
```

- `--imap_endpoint`: The IMAP server endpoint (e.g., `imap.gmail.com`).
- `--smtp_endpoint`: The SMTP server endpoint (e.g., `smtp.gmail.com`).
- `--smtp_port`: The port number for the SMTP server (e.g., `587` for Gmail).
- `--from_email_filter`: Filter emails from a specific sender i.e lab fax email etc.

