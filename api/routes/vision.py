"""
Vision API routes for image analysis using Claude
"""
import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import anthropic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["vision"])

class ImageAnalysisRequest(BaseModel):
    imageBase64: str
    mimeType: str
    prompt: str

class ImageAnalysisResponse(BaseModel):
    response: str

@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analyze an image using Claude's vision capabilities
    
    Supports:
    - Image description
    - Text extraction (OCR)
    - Visual question answering
    """
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": request.mimeType,
                                "data": request.imageBase64,
                            },
                        },
                        {
                            "type": "text",
                            "text": request.prompt
                        }
                    ],
                }
            ],
        )
        
        logger.info(f"Image analyzed successfully with prompt: {request.prompt[:50]}...")
        
        return ImageAnalysisResponse(
            response=message.content[0].text
        )
        
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        raise HTTPException(status_code=502, detail=f"Claude API error: {str(e)}")
    except Exception as e:
        logger.error(f"Image analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
