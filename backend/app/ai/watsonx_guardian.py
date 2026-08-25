"""
Granite Guardian Content Safety Screening

Wraps the Granite Guardian model for content safety screening of
AI-generated compliance reports before serving them to users.

Architecture: Every generated report is screened before being returned.
If the Guardian model is unavailable, the report is not served (counted
as a safety failure, per the /judges transparency endpoint).

If watsonx.ai is not configured, this module logs a warning and
returns a conservative "not screened" result.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class GuardianResult:
    """Result from Granite Guardian content safety screening."""

    def __init__(
        self,
        screened: bool,
        safe: bool,
        reason: str,
        model: str = "",
    ) -> None:
        self.screened = screened  # Whether screening was performed
        self.safe = safe          # Whether content is safe
        self.reason = reason      # Guardian's explanation
        self.model = model

    def to_dict(self) -> dict:
        return {
            "screened": self.screened,
            "safe": self.safe,
            "reason": self.reason,
            "model": self.model,
        }


def screen_report(report_text: str) -> GuardianResult:
    """
    Screen a compliance report for content safety using Granite Guardian.

    Per the /judges transparency endpoint specification:
    "A safety screen that could not run counts as a failure."

    If watsonx.ai is unavailable, the report is flagged as "not screened"
    and will not be returned to the user unless fallback mode is enabled.
    """
    from app.ai.watsonx_client import get_watsonx_client

    client = get_watsonx_client()

    if not client.is_available():
        logger.warning(
            "Granite Guardian not available. Report not screened. "
            "Configure WATSONX_API_KEY and WATSONX_PROJECT_ID to enable safety screening."
        )
        return GuardianResult(
            screened=False,
            safe=False,  # Conservative: treat unscreened as unsafe
            reason="Safety screening unavailable: watsonx.ai not configured.",
            model="",
        )

    result = client.screen_content(report_text)
    if result is None:
        return GuardianResult(
            screened=False,
            safe=False,
            reason="Safety screening failed: Guardian model returned no response.",
            model="",
        )

    return GuardianResult(
        screened=True,
        safe=result.get("safe", False),
        reason=result.get("reason", ""),
        model=result.get("model", ""),
    )
