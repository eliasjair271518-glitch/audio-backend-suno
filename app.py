from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pedalboard import Pedalboard, Compressor, Limiter, Gain
from pedalboard.io import AudioFile

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
    return {"status": "Servidor de audio activo y listo para masterizar"}

@app.post("/procesar/")
async def procesar_audio(file: UploadFile = File(...)):
    input_filename = file.filename
    input_path = f"/tmp/{input_filename}"
    output_path = f"/tmp/Mastered_{input_filename}"
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        with AudioFile(input_path) as f:
            audio = f.read(f.frames)
            samplerate = f.samplerate

        board = Pedalboard([
            Compressor(threshold_db=-16.0, ratio=2.5, attack_ms=15.0, release_ms=100.0),
            Gain(gain_db=2.0),
            Limiter(threshold_db=-1.0, release_ms=100.0)
        ])

        effected = board(audio, samplerate)

        with AudioFile(output_path, 'w', samplerate, effected.shape) as f:
            f.write(effected)
            
    except Exception as e:
        print(f"Error en el procesamiento: {e}")
        output_path = input_path

    return FileResponse(
        path=output_path, 
        media_type="audio/mpeg", 
        filename=f"Mastered_{input_filename}"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
