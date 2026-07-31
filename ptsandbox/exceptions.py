class SandboxException(Exception):
    """Base exception for all custom errors raised by the library."""


class SandboxUploadException(SandboxException):
    """Raised when uploading one or more files to the sandbox fails."""


class SandboxTooManyErrorsException(SandboxException):
    """Raised by ``wait_for_report`` when the number of consecutive errors
    while polling for a scan result exceeds the configured ``error_limit``."""


class SandboxWaitTimeoutException(SandboxException):
    """Raised by ``wait_for_report`` when the scan result is not ready
    within the specified ``wait_time``."""
