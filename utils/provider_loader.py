from importlib import import_module
from typing import Dict
from providers.base import PaymentProvider
from config import settings

def load_payment_providers() -> Dict[str, PaymentProvider]:
    providers = {}
    for provider_key, provider_config in settings.payment_providers.items():
        module_path, class_name = provider_config.class_path.rsplit('.', 1)
        module = import_module(module_path)
        provider_class = getattr(module, class_name)
        providers[provider_key] = provider_class(**provider_config.config)
    return providers