from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Servidor de audio activo y listo"}

@app.post("/procesar/")
async def procesar_audio(file: UploadFile = File(...)):
    input_filename = file.filename
    input_path = f"/tmp/{input_filename}"
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    output_path = input_path 
    output_filename = f"Mastered_{input_filename}"

    return FileResponse(
        path=output_path, 
        media_type="audio/mpeg", 
        filename=output_filename
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
