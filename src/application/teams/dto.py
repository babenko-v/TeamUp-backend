from typing import Optional

from pydantic import BaseModel, constr

class TeamDTO(BaseModel):
    name: constr(min_length=3, max_length=50)
    description: constr(min_length=10, max_length=500)
    avatar_url: Optional[constr(min_length=10, max_length=500)]

class UpdateTeamDTO(BaseModel):
    name: Optional[constr(min_length=3, max_length=50)] = None
    description: Optional[constr(min_length=10, max_length=500)] = None
    avatar_url: Optional[constr(min_length=10, max_length=500)] = None

