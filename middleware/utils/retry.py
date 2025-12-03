import time
import asyncio
from typing import Callable, Any, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

async def retry_with_backoff(
    func: Callable,
    *args,
    max_retries: int = None,
    initial_delay: float = None,
    **kwargs
) -> Any:
    """
    Reintenta una función asíncrona con exponential backoff
    """
    max_retries = max_retries or settings.MAX_RETRIES
    delay = initial_delay or settings.RETRY_DELAY
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)
                logger.warning(
                    f"Intento {attempt + 1}/{max_retries} falló: {str(e)}. "
                    f"Reintentando en {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Todos los reintentos fallaron: {str(e)}")
    
    raise last_exception
