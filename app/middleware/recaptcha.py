from fastapi import HTTPException, status, Request
from typing import Optional, Callable
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

def create_recaptcha_dependency(
    min_score: float = 0.5,
    action: Optional[str] = None
):
    """
    Factory function to create reCAPTCHA dependency with custom parameters
    
    Args:
        min_score: Minimum score threshold for reCAPTCHA v3
        action: Expected action name for verification
    
    Returns:
        FastAPI dependency function
    """
    async def dependency(request: Request) -> bool:
        return await verify_recaptcha_dependency(
            request=request,
            min_score=min_score,
            action=action
        )
    
    return dependency

# Pre-configured dependencies for different security levels
verify_recaptcha_high = create_recaptcha_dependency(min_score=0.8, action="high_security")
verify_recaptcha_medium = create_recaptcha_dependency(min_score=0.5, action="medium_security")
verify_recaptcha_low = create_recaptcha_dependency(min_score=0.3, action="low_security")

# Specific action dependencies
verify_recaptcha_register = create_recaptcha_dependency(min_score=0.7, action="register")
verify_recaptcha_login = create_recaptcha_dependency(min_score=0.5, action="login")
verify_recaptcha_search = create_recaptcha_dependency(min_score=0.4, action="search")