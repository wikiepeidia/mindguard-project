"""Centralized privacy policy for sensitive identifier display."""

MASKED_DATA_NOTICE = "Du lieu da duoc che de bao mat"


def can_view_full_sensitive(is_admin) -> bool:
    """Only admins can view full sensitive identifiers."""
    return bool(is_admin)


def mask_phone_keep_last3(value: str) -> str:
    """Mask all characters except last 3 for phone-like identifiers."""
    raw = "" if value is None else str(value)
    if len(raw) <= 3:
        return raw
    return "*" * (len(raw) - 3) + raw[-3:]


def mask_identifier_keep_2_2(value: str) -> str:
    """Mask non-phone identifiers by keeping first 2 and last 2 chars."""
    raw = "" if value is None else str(value)
    length = len(raw)

    if length <= 2:
        return raw
    if length == 3:
        return f"{raw[0]}*{raw[-1]}"
    if length <= 4:
        return raw

    return f"{raw[:2]}{'*' * (length - 4)}{raw[-2:]}"


def to_display_identifier(raw_identifier: str, report_type: str = "general", is_admin: bool = False) -> str:
    """Return role-safe identifier according to report type and viewer role."""
    if can_view_full_sensitive(is_admin):
        return "" if raw_identifier is None else str(raw_identifier)

    report_kind = (report_type or "").strip().lower()
    if report_kind in {"general", "phone"}:
        return mask_phone_keep_last3(raw_identifier)
    return mask_identifier_keep_2_2(raw_identifier)
