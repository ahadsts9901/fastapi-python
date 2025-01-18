import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from firebase_admin import credentials, storage, initialize_app
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize Firebase
cred = credentials.Certificate("simple-database-b15ab-firebase-adminsdk-vbe7e-2c49ecc0e9.json")  # Replace with your service account key path
firebase_bucket = os.getenv("FIREBASE_BUCKET")
initialize_app(cred, {
    "storageBucket": firebase_bucket  # Replace with your Firebase Storage bucket URL
})

# Firebase storage bucket
bucket = storage.bucket()

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    try:
        # Create a blob in the bucket
        blob = bucket.blob(file.filename)

        # Upload the file to Firebase Storage
        blob.upload_from_file(file.file)

        # Optionally, make the file public and get its URL
        blob.make_public()
        file_url = blob.public_url

        return JSONResponse(
            status_code=200,
            content={"message": "File uploaded successfully", "url": file_url},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
