import typing
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi_rest_jsonapi.request.request_context import RequestContext


class Response(JSONResponse):
    def __init__(
        self,
        request_ctx: RequestContext,
        content: typing.Any = None,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background: BackgroundTasks = None,
    ) -> None:
        self.request_ctx = request_ctx
        super().__init__(content, status_code, headers, media_type, background)

    def get_pagination_links(self):
        links = {}
        links["self"] = self.request_ctx.page.get_self_link()
        links["first"] = self.request_ctx.page.get_first_link()
        links["prev"] = self.request_ctx.page.get_prev_link()
        links["next"] = self.request_ctx.page.get_next_link()
        links["last"] = self.request_ctx.page.get_last_link()
        return links

    def render(self, content: typing.Any) -> bytes:
        if self.request_ctx.page.is_paginated():
            content["links"] = self.get_pagination_links()

        return super().render(content)
