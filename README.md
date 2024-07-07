# About
POC for an automated system extracting invoice data from mail attachments using computer vision, and sending the extracted data to a Google Sheet for further analysis by business teams.

# Objective
Invoices are key elements in most business activities. However, more often than not, invoices are pdf files that are not considered "structured" data-wise: it can be a challenge to leverage invoice data for analysis purposes as it would require extracting said data beforehand, costing time and effort when the extraction is done manually.<br>
That's where an automated data extraction system comes in handy.
When a company has a dedicated mail address for invoices (e.g. invoice@mycompany.com), it can be beneficial to set up a system that automatically extracts invoice data from new mails. Extracted data can then be added to a Google Sheet for further analysis by business teams.

# Tools
- Gmail
- Google Sheets
- [GAS (Google App Script)](https://www.google.com/script/start/)
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [AWS API Gateway](https://aws.amazon.com/api-gateway/)
- [OpenAI chat completion API](https://platform.openai.com/docs/api-reference/chat/create)
- Python libraries: [Flask](https://flask.palletsprojects.com/en/3.0.x/), [PyMuPdf](https://pymupdf.readthedocs.io/en/latest/index.html)

# Requirements

The following table lists the requirements taken into account for the system design.<br>
Since this is a POC, not all the requirements were implemented in the development.

| Number | Requirement | Description |
|-------|-------------|--------------|
| 1 | Process "unread" mails | The "unread" status is what indicates to the script that the mail is "new" and must be processed. |
| 2 | Mark "unread" mails as "read" after being processed | Ensures that the mail won't be processed again by the next script execution. |
| 3 | Extract mail subject | In the destination file/database, each record must contain the mail subject. The subject can be used to easily find a mail and perform a manual check if necessary. |
| 4 | Process mails with single or multiple attachments | When a mail contains multiple attachments, the script must be able to process all the attachments. |
| 5 | Process multiple attachments individually | When a mail contains multiple attachments, the script must be able to process every attachment individually, one after another. |
| 6 | Process an attachment with a single page or multiple pages | When an attachment contains multiple pages, the script must be able to process every page to extract the correct data. |
| 7 | Cancel processing if the attachment is not a pdf file | The script only accepts pdf file as input. |
| 8 | Cancel processing if the attachment is not an invoice | When passed to the OpenAI completion chat API, the model must check the input file to verify that it's an invoice. If the input file is not recognized as an invoice, the model must not return any data. Otherwise, the processing can continue. |
| 9 | Cancel processing if the invoice record already exists in the destination file/database | When the invoice identifier has been extracted, the script must check that the identifier doesn't already exist in the destination file/database. If it already exists, processing must be cancelled and no data will be added to the destination file/database. |
| 10 | Cancel processing if the data cannot be extracted successfully | If the OpenAI completion chat API doesn't return any data, then the processing must be cancelled, no data will be added to the destination file/database. |
| 11 | Cancel processing if the data extracted doesn't have the correct output format | If the OpenAI completion chat API returns data with an incorrect output structure, then the processing must be cancelled and no data will be added to the destination file/database. |
| 12 | Save error event in an error log when processing is canceled | When a processing is cancelled, the event must be saved in an error log describing the error type.<br> Error types: <ul><li>1) Wrong file format: not a pdf file <li>2) Wrong file type: not an invoice <li>3) Data couldn't be extracted: no data returned <li>4) Wrong output format: output must be as follows: {'identifier': 'INVO-005', 'amount': '425'} <li>5) Duplicate entry: invoice identifier already exists in the destination file/database. Identifier: {identifier}. Amount from database: {amount}. Amount from processed mail: {amount}"</ul> |



# Process

## Functional overview

Below is the overview describing how the system works on a functional level.

<b>Steps</b>:
1) New mail received in the invoice mail address (e.g. invoice@mycompany.com)
2) Every 5 minutes, the script checks for unread mails
3) For each unread mail, the script retrieves data from the invoice attachment: extracting invoice identifier and total amount
4) Extracted data is added to a Google Sheet
5) The unread mail is marked as read

## Technical overview

Below is the overview describing how the system works on a technical level.

The script runs every 5 minutes with the built-in trigger system in GAS.<br>
The invoice processing is done in Python with PyMuPdf and the OpenAI chat completion API: the pdf file is encoded as a base64 string, and passed to the OpenAI API to extract the information.<br>
This invoice processing step is turned into an API with Flask and hosted on AWS with Lambda and API Gateway, so that it can be accessed with the `/invoice` endpoint on GAS through the `UrlFetchApp.fetch()` method.<br>

See script files in the repository:
1) [GAS script](/gas.js)
2) [Lambda Flask API script](/lambda_function.py)
3) [Jupyter processing workflow script](/invoice_processing_workflow.ipynb)

<b>Steps</b>:
1) New mail received in the invoice mail address (e.g. invoice@mycompany.com)
2) Every 5 minutes, the script checks for unread mails
3) For each unread mail, the script retrieves the attachment (invoice pdf file)
4) Invoice pdf file is converted to a pdf base64 string
5) Pdf base64 string is passed as a payload to the  `/invoice` API endpoint
6) In the `/invoice` API, the pdf base64 string is transformed into a png base64 string with PyMuPdf so that it can be passed to the OpenAI completion chat API
7) Png base64 string is passed to the OpenAI completion chat API
8) OpenAI completion chat API extracts the invoice identifier and total amount and returns it as a json output
9) Finally, the `/invoice` API returns the invoice identifier and total amount
10) Returned data is added to a Google Sheet
11) The unread mail is marked as read

<b>Diagram</b>

![Test](/diagram.png)

# Demo

https://github.com/FlorianLD/invoice_data_extraction/assets/156505562/40453c74-6236-4ad8-80f1-5cac88ae89f3
