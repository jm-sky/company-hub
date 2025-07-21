import httpx
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class ReCaptchaVerificationResponse(BaseModel):
    """reCAPTCHA verification response model"""
    success: bool
    score: Optional[float] = None
    action: Optional[str] = None
    challenge_ts: Optional[str] = None
    hostname: Optional[str] = None
    error_codes: Optional[list] = None

class ReCaptchaService:
    """Google reCAPTCHA verification service"""
    
    def __init__(self):
        self.secret_key = settings.recaptcha_secret_key
        self.verify_url = settings.recaptcha_verify_url
        self.min_score = settings.recaptcha_min_score
        self.timeout = settings.recaptcha_timeout
        self.enabled = settings.recaptcha_enabled
    
    async def verify_token(
        self, 
        token: str, 
        remote_ip: Optional[str] = None
    ) -> ReCaptchaVerificationResponse:
        """
        Verify reCAPTCHA token with Google API
        
        Args:
            token: The reCAPTCHA response token
            remote_ip: The user's IP address (optional)
        
        Returns:
            ReCaptchaVerificationResponse with verification details
        """
        if not self.enabled:
            logger.info("reCAPTCHA verification disabled, returning success")
            return ReCaptchaVerificationResponse(success=True, score=1.0)
        
        if not self.secret_key:
            logger.error("reCAPTCHA secret key not configured")
            return ReCaptchaVerificationResponse(
                success=False, 
                error_codes=["missing-secret-key"]
            )
        
        try:
            data = {
                "secret": self.secret_key,
                "response": token,
            }
            
            if remote_ip:
                data["remoteip"] = remote_ip
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.verify_url,
                    data=data
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"reCAPTCHA verification result: {result}")
                
                return ReCaptchaVerificationResponse(**result)
                
        except httpx.TimeoutException:
            logger.error("reCAPTCHA verification timeout")
            return ReCaptchaVerificationResponse(
                success=False, 
                error_codes=["timeout-or-duplicate"]
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"reCAPTCHA HTTP error: {e}")
            return ReCaptchaVerificationResponse(
                success=False, 
                error_codes=["http-error"]
            )
        except Exception as e:
            logger.error(f"reCAPTCHA verification error: {e}")
            return ReCaptchaVerificationResponse(
                success=False, 
                error_codes=["unknown-error"]
            )
    
    async def validate_score(
        self, 
        token: str, 
        min_score: Optional[float] = None,
        action: Optional[str] = None,
        remote_ip: Optional[str] = None
    ) -> bool:
        """
        Validate reCAPTCHA token and check if score meets threshold
        
        Args:
            token: The reCAPTCHA response token
            min_score: Minimum score threshold (defaults to config value)
            action: Expected action name for verification
            remote_ip: The user's IP address (optional)
        
        Returns:
            True if verification passes and score meets threshold
        """
        if not self.enabled:
            return True
        
        verification = await self.verify_token(token, remote_ip)
        
        if not verification.success:
            logger.warning(f"reCAPTCHA verification failed: {verification.error_codes}")
            return False
        
        # Check score threshold for v3
        if verification.score is not None:
            threshold = min_score if min_score is not None else self.min_score
            if verification.score < threshold:
                logger.warning(
                    f"reCAPTCHA score {verification.score} below threshold {threshold}"
                )
                return False
        
        # Verify action if provided
        if action and verification.action != action:
            logger.warning(
                f"reCAPTCHA action mismatch: expected {action}, got {verification.action}"
            )
            return False
        
        logger.info(f"reCAPTCHA validation successful with score {verification.score}")
        return True
    
    def get_error_message(self, error_codes: Optional[list]) -> str:
        """Get human-readable error message from error codes"""
        if not error_codes:
            return "reCAPTCHA verification failed"
        
        error_messages = {
            "missing-input-secret": "The secret parameter is missing",
            "invalid-input-secret": "The secret parameter is invalid or malformed",
            "missing-input-response": "The response parameter is missing",
            "invalid-input-response": "The response parameter is invalid or malformed",
            "bad-request": "The request is invalid or malformed",
            "timeout-or-duplicate": "The response is no longer valid",
            "http-error": "HTTP error occurred during verification",
            "unknown-error": "Unknown error occurred",
            "missing-secret-key": "reCAPTCHA secret key not configured"
        }
        
        messages = [error_messages.get(code, code) for code in error_codes]
        return "; ".join(messages)

# Global reCAPTCHA service instance
recaptcha_service = ReCaptchaService()