import random

from app.core.config import settings
from app.core.enums import ServiceType

_fail_counters = {
    ServiceType.USER: 0,
    ServiceType.PAYMENT: 0,
    ServiceType.COMMUNICATION: 0,
}


def simulate_failure(service_enum: ServiceType):
    """
    Simulate deterministic forced failures up to FORCE_SERVICE_FAILURES.
    Then fallback to random transient failures.
    """

    if _fail_counters[service_enum] < settings.FORCE_SERVICE_FAILURES:
        _fail_counters[service_enum] += 1
        raise Exception(f"Forced simulated failure for {service_enum.value}")

    if settings.ENABLE_RANDOM_FAILURES:
        if random.choice([True, False]):
            raise Exception(
                f"Random simulated transient failure for {service_enum.value}"
            )
