from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import librosa
import soundfile as sf
from pedalboard import Pedalboard, Compressor, Limiter, Gain

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
    return {"status": "Servidor activo - Soporte para MP3 y WAV"}

@app.post("/procesar/")
async def procesar_audio(file: UploadFile = File(...)):
    input_filename = file.filename
    input_path = f"/tmp/{input_filename}"
    base_name, ext = os.path.splitext(input_filename)
    
    # Archivo de salida masterizado en alta calidad WAV
    output_path = f"/tmp/Mastered_{base_name}.wav"
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # librosa lee y decodifica automáticamente tanto MP3 como WAV
        audio, samplerate = librosa.load(input_path, sr=None, mono=False)

        # Cadena de masterización profesional con Pedalboard
        board = Pedalboard([
            Compressor(threshold_db=-16.0, ratio=2.5, attack_ms=15.0, release_ms=100.0),
            Gain(gain_db=2.0),
            Limiter(threshold_db=-1.0, release_ms=100.0)
        ])

        # Procesamos el audio de cualquiera de los dos formatos
        effected = board(audio, samplerate)

        # Guardamos el resultado procesado
        if effected.ndim == 2:
            sf.write(output_path, effected.T, samplerate)
        else:
            sf.write(output_path, effected, samplerate)
            
    except Exception as e:
        print(f"Error en el procesamiento: {e}")
        output_path = input_path

    return FileResponse(
        path=output_path, 
        media_type="audio/wav", 
        filename=f"Mastered_{base_name}.wav"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
