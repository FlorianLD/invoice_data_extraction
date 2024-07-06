// Main function checking unread mails and retrieving data from the invoice pdf attachment
function get_mail() {
    try {
      const threads = GmailApp.search('is:unread', 0, 1);
      const msgs = GmailApp.getMessagesForThreads(threads);
      for (let i = 0 ; i < msgs.length; i++) {
        for (let j = 0; j < msgs[i].length; j++) {
          const attachments = msgs[i][j].getAttachments();
          for (let k = 0; k < attachments.length; k++) {
          console.log('Attachment: ',attachments[k].getName());
  
          const attachment_base64 = to_base64(attachments[k]);
          const invoice_data = get_data(attachment_base64);
  
          console.log('API returned the following data: \n',invoice_data);
          console.log('Identifier: ',invoice_data.identifier);
          console.log('Amount: ',invoice_data.amount);
  
          to_sheet(invoice_data);
          }
        }
        GmailApp.markThreadRead(threads[i])
      }
    }
  
    catch (err) {
      console.error('An error occurred:', err);
    }
  }
  
  // Transforming the invoice pdf file into a base64 string
  function to_base64 (attachment) {
    try {
      const bytes = attachment.getBytes();
      const attachment_base64 = Utilities.base64Encode(bytes).toString();
      return attachment_base64;
      }
  
    catch (err) {
      console.log('An error occurred', err);
      throw err;
    }
  }
  
  // Processing the pdf base64 string through our /invoice API endpoint to retrieve invoice identifier and total amount
  function get_data(base64_string) {
    const url = `${baseUrl}/invoice`
    
    // Define the JSON payload
    const data = {
      "base64_string": base64_string,
      "isBase64Encoded": true
    };
  
    // Define the headers
    const headers = {
      'Content-Type': 'application/json'
    };
  
    // Define the options for the request
    const options = {
      'method': 'post',
      'headers': headers,
      'payload': JSON.stringify(data),
      'muteHttpExceptions': true
    };
  
    try {
      const response = UrlFetchApp.fetch(url, options);
      const responseText = response.getContentText();
      const jsonResponse = JSON.parse(responseText);
      return jsonResponse
    } 
    catch (err) {
      console.error('Error during API request:', err);
      throw err;
    }
  }
  
  // Adding invoice data to a google sheet
  function to_sheet(invoice_data) {
    try {
      const ss = SpreadsheetApp.openByUrl(gsheetUrl);
      const sheet = ss.getSheets()[0];
      const range = sheet.getRange('A2:B2');
  
      range.insertCells(SpreadsheetApp.Dimension.ROWS);
  
      const values = [invoice_data.identifier, invoice_data.amount];
  
      console.log('Length of values array is 2:',values.length == 2);
      console.log('Array: ',[values]);
  
      range.setValues([values]);
      }
  
    catch (err) {
      console.log('An error occurred', err)
      throw err;
      }
    }