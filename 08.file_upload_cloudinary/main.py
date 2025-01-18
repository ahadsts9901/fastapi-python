import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),  # Replace with your Cloudinary cloud name
    api_key=os.getenv("CLOUDINARY_API_KEY"),       # Replace with your Cloudinary API key
    api_secret=os.getenv("CLOUDINARY_API_SECRET"), # Replace with your Cloudinary API secret
)


@app.post("/api/v1/upload")
async def upload_file(file: UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    try:
        # Upload the file to Cloudinary
        result = cloudinary.uploader.upload(file.file)

        # Return the URL of the uploaded file
        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded successfully",
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "version": result["version"]
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
