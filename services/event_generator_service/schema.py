from pydantic import BaseModel
from typing import Dict, Union 
from datetime import datetime



class FeaturesEvent(BaseModel):
    features: Dict[str, Union[datetime, float, int, str, bool]]
    