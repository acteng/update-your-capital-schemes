from __future__ import annotations

from typing import Any, Callable

from wtforms.fields.numeric import IntegerField
from wtforms.form import BaseForm


class CustomMessageIntegerField(IntegerField):
    """
    An integer field that allows the error message for invalid values to be customised.
    """

    def __init__(
        self,
        label: str | None = None,
        validators: tuple[Callable[[BaseForm, CustomMessageIntegerField], object], ...] | list[Any] | None = None,
        message: str = "Not a valid integer value.",
        **kwargs: Any,
    ):
        super().__init__(label, validators, **kwargs)
        self.message = message

    def process_data(self, value: Any) -> None:
        if value is not None:
            self._check_valid(value)

        super().process_data(value)

    def process_formdata(self, valuelist: list[Any]) -> None:
        if valuelist:
            self._check_valid(valuelist[0])

        super().process_formdata(valuelist)

    def _check_valid(self, value: Any) -> None:
        try:
            int(value)
        except ValueError:
            raise ValueError(self.message)
