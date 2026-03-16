from app.service import get_data

def handler(request):
    """
    Cloud Function entry point that handles incoming HTTP requests, retrieves the latest data using the get_data function, and returns it as a JSON response.
    """
    data = get_data(mode="latest")
    return data