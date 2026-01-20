"""FastAPI backend for The Drunken Bot lyric autocomplete."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging

from app.core.config import get_settings
from app.core.text_utils import clean_completion
from app.services.vllm_client import vllm_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Lyric autocomplete service powered by vLLM",
    version=settings.version,
    debug=settings.debug
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompletionRequest(BaseModel):
    """Request model for lyric completion."""
    text: str = Field(..., min_length=1, description="Input text to complete")
    max_tokens: int = Field(
        default=settings.default_max_tokens,
        ge=1,
        le=settings.max_allowed_tokens,
        description="Maximum tokens to generate"
    )
    temperature: float = Field(
        default=settings.default_temperature,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )

class CompletionResponse(BaseModel):
    """Response model for lyric completion."""
    completion: str = Field(..., description="Generated completion text")
    raw_completion: str = Field(..., description="Raw model output before cleaning")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": settings.app_name,
        "status": "running",
        "version": settings.version,
        "vllm_url": settings.vllm_url,
        "model": settings.model_name
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version
    }

@app.post("/complete", response_model=CompletionResponse)
async def complete_lyrics(request: CompletionRequest):
    """
    Generate lyric completions for the given input text.
    
    This endpoint:
    1. Sends the input to vLLM for completion
    2. Cleans the output (removes <think> tags, handles overlap)
    3. Returns the cleaned completion
    
    Returns a CompletionResponse with both cleaned and raw completions.
    """
    try:
        logger.info(f"Completion request: '{request.text[:50]}...' "
                   f"(max_tokens={request.max_tokens}, temp={request.temperature})")
        
        # Call vLLM service
        raw_completion = await vllm_client.generate_completion(
            prompt=request.text,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Clean the completion using your utilities
        cleaned_completion = clean_completion(request.text, raw_completion)
        
        logger.info(f"Completion generated: '{cleaned_completion[:50]}...'")
        
        return CompletionResponse(
            completion=cleaned_completion,
            raw_completion=raw_completion
        )
        
    except Exception as e:
        logger.error(f"Completion failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Completion generation failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
