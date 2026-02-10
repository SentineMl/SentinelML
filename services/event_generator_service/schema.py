from pydantic import BaseModel
from typing import Dict, Union 
from datetime import datetime



class FeaturesEvent(BaseModel):
    timestamp: datetime
    features: Dict[str, Union[float, int, str, bool]]
    