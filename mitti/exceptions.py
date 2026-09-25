class RequestValidationError(Exception):
    def __init__(self, source: str, parameter: str, detail: str) -> None:
        self.source = source
        self.parameter = parameter
        self.detail = detail
        super().__init__(f"Invalid {source} parameter '{parameter}': {detail}")
