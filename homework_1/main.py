import json
import math

# uvicorn main:app
# pytest test_homework_1.py
async def app(scope, receive, send):
    assert scope["type"] == "http"

    # factorial query
    if scope["path"] == "/factorial" and scope["method"] == "GET":
        query_line = scope["query_string"].decode("utf-8")
        n_value = dict(elem.split("=") for elem in query_line.split("&") if "=" in elem)
        
        if "n" in n_value:
            try:
                num = int(n_value["n"])
                if num >= 0:
                    response = math.factorial(num)
                    status_code = 200
                else:
                    response = "Value less than 0"
                    status_code = 400
            except:
                response = "No number given"
                status_code = 422
        else:
            response = "No number given"
            status_code = 422
    
    # fibonacci query 
    elif scope["path"].startswith("/fibonacci")  and scope["method"] == "GET":
        try:
            path_num = scope["path"].split("/")
            fib_num = int(path_num[2])
            if fib_num >= 0:
                response = fibonacci(fib_num)
                status_code = 200
            else:
                response = "Value less than 0"
                status_code = 400
        except (ValueError, IndexError):
            response = "Not a number or no number provided"
            status_code = 422
    
    # mean query
    elif scope["path"] == "/mean" and scope["method"] == "GET":
        get_body = await read_body(receive)
        try:
            array = json.loads(get_body)
            if not isinstance(array, list) or not all(
                isinstance(x, (int, float)) for x in array):
                response = "The given array has the not float entities"
                status_code = 422
            elif not array: 
                response = "The given array is empty"
                status_code = 400
            else:
                mean_num= sum(array) / len(array) 
                response = mean_num
                status_code = 200
        except json.JSONDecodeError:
            response = "Invalid JSON format"
            status_code = 422

    
    else:
        response = "Not found"
        status_code = 404

    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": json.dumps({"result": response}).encode("utf-8"),
        }
    )
            
# fibonacci function
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# fucntion to read the body of the response 
async def read_body(receive):
    body = b''
    more_body = True

    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)

    return body
