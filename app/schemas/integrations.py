from typing import Dict, Optional
from pydantic import BaseModel, RootModel

from app.core.enums import IntegrationHealthStatus


class ServiceIntegrationStatus(BaseModel):
    last_success: Optional[str]
    last_event_id: Optional[str]
    status: IntegrationHealthStatus

class IntegrationStatusResponse(RootModel[Dict[str, ServiceIntegrationStatus]]):
    pass
