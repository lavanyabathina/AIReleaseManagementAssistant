from app.security.security_config import (
        ALLOWED_CONFLUENCE_SPACES
)


def authorize_confluence_space(confluence_space: str):
    if confluence_space.lower() not in ALLOWED_CONFLUENCE_SPACES:
        raise PermissionError(f"Confluence Space {confluence_space} is not authorized.")




