import json
import os
import azure.functions as func
import logging
from openai import AzureOpenAI

app = func.FunctionApp()

# AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
# AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION")

# client = AzureOpenAI(
#     api_key=AZURE_OPENAI_KEY,
#     api_version=AZURE_OPENAI_VERSION,
#     azure_endpoint = AZURE_OPENAI_ENDPOINT
# )

@app.function_name(name="HttpTrigger1")
@app.route(route="hello", auth_level=func.AuthLevel.ANONYMOUS)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    return func.HttpResponse(
        "This HTTP triggered function executed successfully.",
        status_code=200
        )

# @app.function_name(name="myfunc")
# @app.service_bus_queue_trigger(
#     arg_name="msg",
#     queue_name="input",
#     connection="ServiceBusConnection__fullyQualifiedNamespace",
# )
# def test_function(msg: func.ServiceBusMessage):
#     # whatever, just logging to see if it gets invoked
#     pass

@app.function_name(name="myfunc2")
@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="input",
    connection="ServiceBusConnection__fullyQualifiedNamespace",
)
def test_function2(msg: func.ServiceBusMessage):
    # whatever, just logging to see if it gets invoked
    pass


@app.function_name(name="detect_objects")
@app.service_bus_queue_trigger(arg_name="input", queue_name="input", connection="ServiceBusConnection__fullyQualifiedNamespace")
@app.service_bus_topic_output(arg_name="output", queue_name="output", connection="ServiceBusConnection__fullyQualifiedNamespace")
def detect_objects(input: func.ServiceBusMessage, output: func.Out[str]):
    event_string = input.get_body().decode('utf-8')
    # event = {"topic":"/subscriptions/977171a9-6bfd-49c4-a496-018d3312466e/resourceGroups/azure-openai/providers/Microsoft.Storage/storageAccounts/stfunctionsopenai","subject":"/blobServices/default/containers/sources/blobs/_636d5f92-d15d-4d13-905e-fd17b09aacc5.jpeg","eventType":"Microsoft.Storage.BlobCreated","id":"695addc9-401e-00db-75bb-e174ef061cf8","data":{"api":"PutBlob","clientRequestId":"87083d28-f4a8-482b-ae17-e41aae222009","requestId":"695addc9-401e-00db-75bb-e174ef000000","eTag":"0x8DCAFD2E44A1357","contentType":"image/jpeg","contentLength":256569,"blobType":"BlockBlob","url":"https://stfunctionsopenai.blob.core.windows.net/sources/_636d5f92-d15d-4d13-905e-fd17b09aacc5.jpeg","sequencer":"00000000000000000000000000009D950000000000501908","storageDiagnostics":{"batchId":"8acc52d3-6006-0075-00bb-e1d9fe000000"}},"dataVersion":"","metadataVersion":"1","eventTime":"2024-07-29T13:32:28.7820631Z"}
    logging.info('Python ServiceBus Queue trigger processed a message: %s', event_string)
    event = json.loads(event_string)
    image_url = event['data']['url']
    # Process the image_url as needed
    response = process_image(image_url)

    if hasattr(response, 'choices'):
        print("response.choices is an array with one item or more")
        output.set(str(response.choices[0]))
    else:
        print("response.choices is not an array with one item or more")
        output.set("response.choices is not an array with one item or more")

    json_string = str(response.choices[0])
    print(json_string)
    output.set(json_string)

def process_image(image_url):
    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        response_format = {"type": "json_object"},
        messages=[
            { "role": "system", "content": "You are an assistant that detects objects in a list of images and returns the results in JSON Array format."
                                           "For example: {\"tags\": [{\"label\": \"Cars\", \"score\": \"0.9\"}]}" },
            { "role": "user", "content": [
                {
                    "type": "text",
                    "text": "Try to detect the following objects in the list of frames from a video: car, person. Only include the objects that are detected with a certainty above 0.9."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"{image_url}"
                    }
                }
            ] }
        ],
        max_tokens=2000
    )

    print(response)
    return response


# if __name__ == "__main__":
#     detect_objects()
