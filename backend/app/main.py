from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import app.config as config

from app.routes.distance_detection import router as distance_detection_router
from app.routes.face_detection import router as face_detection_router
from app.routes.text_recognition import router as text_recognition_router
from app.routes.product_recognition import router as product_recognition_router


app = FastAPI(title="FastAPI Template", version="1.0.0")

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(distance_detection_router, prefix="/api/distance_detection", tags=["Distance Detection"])
app.include_router(face_detection_router, prefix="/api/face_detection", tags=["Face Detection"])
app.include_router(text_recognition_router, prefix="/api/text_recognition", tags=["Text Recognition"])
app.include_router(product_recognition_router, prefix="/api/product_recognition", tags=["Product Recognition"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Template"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT, reload=True)
