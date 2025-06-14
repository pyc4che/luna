from core.config import settings


def ttl_for(name: str) -> int:
    return settings.get_ttl(f'CACHE_{name.upper()}_TTL')
