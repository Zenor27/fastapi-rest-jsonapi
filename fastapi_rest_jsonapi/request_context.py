from pydantic import BaseModel
from typing import Optional


class RequestContext:
    def __init__(
        self,
        path_parameters: Optional[BaseModel] = None,
        query_parameters: Optional[str] = None,
        body: Optional[dict] = None,
    ) -> None:
        self.path_parameters = path_parameters
        self.query_parameters = query_parameters
        self.body = body
