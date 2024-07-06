from flask import Flask, request, jsonify
import requests
import base64
import fitz
import logging
import json
import os

secret_apikey = os.getenv('OPENAI_API_KEY')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Flask in AWS Lambda!'

@app.route('/test')
def test():
    return 'App is working'

@app.route('/invoice', methods=['POST'])        
def invoice_processing():
    
    # Transform the pdf base64 string into a png base64 string so it can be passed to the openai_request method
    def document_processing(base64_string):
        try:
            pdf_bytes = base64.b64decode(base64_string)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            png_base64_list = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(alpha=True)
                png_bytes = pix.tobytes(output="png")
                png_base64 = base64.b64encode(png_bytes).decode('utf-8')
                png_base64_list.append(png_base64)
            return png_base64_list[0]

        except Exception as e:
            logger.error('Error occurred: %s', e, exc_info=True)
            return jsonify({'error': str(e)}), 500

    
    # Pass the png base64 string to extract the invoice data
    def openai_request(base64_png):
        
        try:
            apikey = secret_apikey
            url = 'https://api.openai.com/v1/chat/completions'

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {apikey}'
            }
            
            data = {
                "model": "gpt-4-turbo",
                "response_format": { "type": "json_object" },
                "messages": [
                {
                    "role": "user",
                    "content": [
                    {
                        "type": "text",
                        "text": "Extract the invoice identifier and the total amount without money symbol. Output must be in a json structure with the following keys: identifier and amount."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_png}"
                        }
                    }
                    ]
                }
                ]
            }
            
            response = requests.post(url=url, headers=headers, json=data)
            
            if response.status_code == 200:
                json_data = response.json()
                content = json_data['choices'][0]['message']['content'] if 'choices' in json_data else None
                return content
            else:
                logger.error(f'Failed to process invoice request. Status code: {response.status_code}, Response: {response.text}')
                return jsonify({'error': 'Failed to process invoice request'}), 500
            
        except Exception as e:
            logger.error('Error occurred: %s', e, exc_info=True)
            return jsonify({'error': str(e)}), 500

    
    # Execute the two methods document_processing and openai_request defined above
    try:
        data = request.get_json()
        base64_string = data.get('base64_string', 'No string provided')

        base64_png = document_processing(base64_string=base64_string)
        result = openai_request(base64_png=base64_png)
        return result
    
    except Exception as e:
        logger.error('Error occurred: %s', e, exc_info=True)
        return jsonify({'error': str(e)}), 500


def lambda_handler(event, context):
    headers = event.get('headers', {})
    query_params = event.get('queryStringParameters', {})
    body = event.get('body', '')

    with app.test_request_context(
        path=event['path'],
        method=event['httpMethod'],
        headers=headers,
        query_string=query_params,
        data=body
    ):
        response = app.full_dispatch_request()

    return {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.get_data(as_text=True)
        }