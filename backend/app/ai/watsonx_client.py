"""
IBM watsonx.ai Client Wrapper

Manages the watsonx.ai SDK connection with token caching.
The IAM token has a 55-minute lifetime; we cache it to avoid
re-authenticating on every request.

Region awareness: different watsonx.ai regions (US-South, EU-DE, etc.)
expose different model catalogs. This client probes for available models
and selects the best fit automatically:

  Instruct priority: ibm/granite-3-1-8b-instruct
                   → meta-llama/llama-3-3-70b-instruct
                   → meta-llama/llama-3-1-8b

  Guardian priority: ibm/granite-guardian-3-8b
                   → ibm/granite-3-1-8b-base (safety prompt)
                   → (graceful no-op if nothing suitable)

  Embedding:         ibm/granite-embedding-278m-multilingual (same in all regions)

If WATSONX_API_KEY or WATSONX_PROJECT_ID are not configured,
all methods return graceful fallbacks. The compliance engine STILL
WORKS without these credentials — only the AI layer is disabled.
"""
from __future__ import annotations

import logging
import time
from functools import lru_cache

logger = logging.getLogger(__name__)

try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    IBM_SDK_AVAILABLE = True
except ImportError:
    IBM_SDK_AVAILABLE = False
    logger.warning("ibm_watsonx_ai SDK not installed. AI features will be disabled.")

# Preferred instruct models in priority order (IBM Granite first, then fallbacks)
# ibm/granite-4-h-small  — IBM Granite, available on US-South, confirmed working
# ibm/granite-3-1-8b-instruct — preferred full instruct (US-South standard plan)
# meta-llama/llama-3-3-70b-instruct — best non-Granite fallback
_INSTRUCT_CANDIDATES = [
    "ibm/granite-3-1-8b-instruct",
    "ibm/granite-4-h-small",
    "ibm/granite-3-2-8b-instruct",
    "ibm/granite-13b-instruct-v2",
    "meta-llama/llama-3-3-70b-instruct",
    "meta-llama/llama-3-1-8b",
    "mistralai/mistral-small-3-1-24b-instruct-2503",
    "meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
]

# Guardian models — ibm/granite-guardian-3-8b is the real Granite Guardian
# It is confirmed available on US-South. Falls back to instruct if unavailable.
_GUARDIAN_CANDIDATES = [
    "ibm/granite-guardian-3-8b",
    "ibm/granite-guardian-3-2b",
    "meta-llama/llama-3-3-70b-instruct",
    "ibm/granite-4-h-small",
    "meta-llama/llama-3-1-8b",
    "mistralai/mistral-small-3-1-24b-instruct-2503",
]


class WatsonxClient:
    """
    Singleton wrapper around the IBM watsonx.ai SDK.
    Auto-detects available models for the connected region.
    """

    def __init__(self) -> None:
        from app.core.config import get_settings
        self._settings = get_settings()
        self._credentials: object | None = None
        self._instruct_model: object | None = None
        self._guardian_model: object | None = None
        self._instruct_model_id: str | None = None
        self._guardian_model_id: str | None = None
        self._initialized = False
        self._last_init_attempt = 0.0
        self._init_retry_interval = 60.0

    def _probe_model(self, candidates: list[str], params: dict) -> tuple[object | None, str | None]:
        """
        Try each candidate model ID until one initialises without error.
        Returns (ModelInference instance, model_id) or (None, None).
        """
        for model_id in candidates:
            try:
                model = ModelInference(
                    model_id=model_id,
                    credentials=self._credentials,
                    project_id=self._settings.watsonx_project_id,
                    params=params,
                )
                # Quick probe: just building the object is enough — actual
                # generation errors are caught per-call.
                logger.info("watsonx.ai: selected model '%s'", model_id)
                return model, model_id
            except Exception as exc:
                logger.debug("Model '%s' unavailable: %s", model_id, exc)
                continue
        return None, None

    def _initialize(self) -> bool:
        """Initialize credentials and probe for available models in this region."""
        if not IBM_SDK_AVAILABLE:
            return False

        if not self._settings.watsonx_configured:
            logger.warning(
                "watsonx.ai not configured: WATSONX_API_KEY and WATSONX_PROJECT_ID required. "
                "AI features will be disabled. Compliance engine runs normally."
            )
            return False

        try:
            self._credentials = Credentials(
                url=self._settings.watsonx_url,
                api_key=self._settings.watsonx_api_key,
            )

            # Probe instruct model
            self._instruct_model, self._instruct_model_id = self._probe_model(
                _INSTRUCT_CANDIDATES,
                {
                    "max_new_tokens": 2048,
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "repetition_penalty": 1.1,
                },
            )

            # Probe guardian model (separate from instruct)
            self._guardian_model, self._guardian_model_id = self._probe_model(
                _GUARDIAN_CANDIDATES,
                {
                    "max_new_tokens": 200,
                    "temperature": 0.0,
                },
            )

            if self._instruct_model is None:
                logger.error(
                    "No supported instruct model found for region %s. "
                    "AI report generation disabled.",
                    self._settings.watsonx_url,
                )
                return False

            self._initialized = True
            logger.info(
                "watsonx.ai ready — instruct: %s, guardian: %s",
                self._instruct_model_id,
                self._guardian_model_id or "unavailable (graceful fallback active)",
            )
            return True

        except Exception as exc:
            logger.error("Failed to initialize watsonx.ai: %s", exc)
            self._initialized = False
            self._last_init_attempt = time.time()
            return False

    def is_available(self) -> bool:
        """Check if watsonx.ai is configured and at least one instruct model is accessible."""
        if not self._initialized:
            now = time.time()
            if now - self._last_init_attempt > self._init_retry_interval:
                self._last_init_attempt = now
                self._initialize()
        return self._initialized

    @property
    def active_instruct_model(self) -> str | None:
        """Return the model ID currently used for text generation."""
        return self._instruct_model_id

    @property
    def active_guardian_model(self) -> str | None:
        """Return the model ID currently used for safety screening."""
        return self._guardian_model_id

    def _chat(self, model: object, system: str, user: str) -> str | None:
        """
        Call the modern /ml/v1/text/chat endpoint via model.chat().
        Falls back to generate_text() if chat() is not available.
        Returns the assistant response text or None on failure.
        """
        try:
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]
            response = model.chat(messages=messages)  # type: ignore[union-attr]
            # Response structure: {"choices": [{"message": {"content": "..."}}]}
            choices = response.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            return None
        except Exception as exc:
            logger.debug("chat() failed, trying generate_text(): %s", exc)
            try:
                return model.generate_text(prompt=f"{system}\n\n{user}")  # type: ignore[union-attr]
            except Exception as exc2:
                logger.error("Both chat() and generate_text() failed: %s", exc2)
                return None

    def generate_text(self, prompt: str, max_tokens: int = 2048) -> str | None:
        """
        Generate text using the best available instruct model.
        Returns None if watsonx.ai is unavailable.
        """
        if not self.is_available() or self._instruct_model is None:
            return None

        try:
            return self._chat(
                self._instruct_model,
                system="You are PHAROS, a satellite orbital compliance expert. Be precise and factual.",
                user=prompt,
            )
        except Exception as exc:
            logger.error("Instruct generation failed (%s): %s", self._instruct_model_id, exc)
            return None

    def screen_content(self, content: str) -> dict | None:
        """
        Screen content for safety.
        Uses Granite Guardian if available, otherwise the instruct model
        with an explicit safety classifier prompt.
        Returns None only if no model is available.
        """
        if not self.is_available():
            return None

        model = self._guardian_model or self._instruct_model
        model_id = self._guardian_model_id or self._instruct_model_id

        if model is None:
            return None

        try:
            # Granite Guardian 3.x uses a binary format:
            #   "No"  = content is NOT unsafe = SAFE
            #   "Yes" = content IS unsafe = UNSAFE
            # Other instruct models use a descriptive SAFE/UNSAFE format.
            if self._guardian_model_id and "guardian" in self._guardian_model_id:
                messages = [{"role": "user", "content": content[:1000]}]
                response_obj = self._guardian_model.chat(messages=messages)  # type: ignore
                choices = response_obj.get("choices", [])
                text = choices[0].get("message", {}).get("content", "").strip() if choices else ""
                # Guardian: "No" = safe, "Yes" = unsafe
                is_safe = text.lower().startswith("no")
                return {
                    "safe": is_safe,
                    "reason": f"Granite Guardian: {'SAFE' if is_safe else 'UNSAFE'} (raw: {text})",
                    "model": self._guardian_model_id,
                }
            else:
                # Instruct model fallback — use descriptive classifier prompt
                system = (
                    "You are a content safety classifier for satellite compliance reports. "
                    "Evaluate if the following text is safe, accurate, and free from harmful content. "
                    "Respond with exactly one word: SAFE or UNSAFE, followed by a colon and a brief reason."
                )
                response = self._chat(model, system=system, user=content[:1000])
                if not response:
                    return None
                is_safe = response.strip().upper().startswith("SAFE")
                return {
                    "safe": is_safe,
                    "reason": response.strip(),
                    "model": model_id,
                }
        except Exception as exc:
            logger.error("Safety screening failed (%s): %s", model_id, exc)
            return None


@lru_cache(maxsize=1)
def get_watsonx_client() -> WatsonxClient:
    """Get the singleton watsonx.ai client."""
    return WatsonxClient()
