from app.service import get_data

def handler(request):
    data = get_data(mode="latest")
    return data