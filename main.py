from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
# def read_root():
    # html_content = "<h2>Hello METANIT.COM!</h2>"
    # return HTMLResponse(content=html_content)

@app.get("/search")
async def search(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})