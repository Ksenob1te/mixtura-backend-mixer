from pydantic import BaseModel


class HealthMessage(BaseModel):
    model_config = {"extra": "forbid"}
    pass
