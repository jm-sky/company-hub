from fastapi import HTTPException, status, Request
from typing import Optional
from app.security.recaptcha import recaptcha_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async def verify_recaptcha_token(
    recaptcha_token: Optional[str],
    request: Request,
    min_score: float = 0.5,
    action: Optional[str] = None
) -> bool:
    """
    Verify reCAPTCHA token
    
    Args:
        recaptcha_token: The reCAPTCHA response token
        request: FastAPI request object
        min_score: Minimum score threshold
        action: Expected action name
    
    Returns:
        True if verification passes
    
    Raises:
        HTTPException: If reCAPTCHA verification fails
    """
    if not settings.recaptcha_enabled:
        logger.info("reCAPTCHA verification disabled")
        return True
    
    if not recaptcha_token:
        logger.warning("reCAPTCHA token missing in request")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reCAPTCHA token is required"
        )
    
    # Get client IP address
    remote_ip = None
    if hasattr(request, 'client') and request.client:
        remote_ip = request.client.host
    
    # Verify reCAPTCHA
    is_valid = await recaptcha_service.validate_score(
        token=recaptcha_token,
        min_score=min_score,
        action=action,
        remote_ip=remote_ip
    )
    
    if not is_valid:
        logger.warning(f"reCAPTCHA verification failed for IP {remote_ip}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reCAPTCHA verification failed. Please try again."
        )
    
    logger.info(f"reCAPTCHA verification successful for IP {remote_ip}")
    return True