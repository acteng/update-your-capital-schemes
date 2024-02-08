from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from wtforms import DateField, Field
from wtforms.fields.numeric import IntegerField
from wtforms.form import BaseForm
from wtforms.validators import Optional, StopValidation


class CustomMessageIntegerField(IntegerField):
    """
    An integer field that allows the error message for invalid values to be customised.

    See: https://github.com/wtforms/wtforms/issues/832
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


class CustomMessageDateField(DateField):
    """
    A date field that allows the error message for invalid values to be customised.

    See: https://github.com/wtforms/wtforms/issues/832
    """

    def __init__(
        self,
        label: str | None = None,
        validators: tuple[Callable[[BaseForm, CustomMessageDateField], object], ...] | list[Any] | None = None,
        format: str = "%Y-%m-%d",
        message: str = "Not a valid date value.",
        **kwargs: Any,
    ):
        super().__init__(label, validators, format, **kwargs)
        self.message = message

    def process_formdata(self, valuelist: list[Any]) -> None:
        if not valuelist:
            return

        date_str = " ".join(valuelist)
        for format in self.strptime_format:
            try:
                self.data = datetime.strptime(date_str, format).date()
                return
            except ValueError:
                self.data = None

        raise ValueError(self.message)


class MultivalueOptional(Optional):
    """
    A validator that allows empty input and supports multivalued fields.

    See: https://github.com/wtforms/wtforms/issues/835
    """

    def __call__(self, form: BaseForm, field: Field) -> None:
        if not field.raw_data or all(self._is_empty(value) for value in field.raw_data):
            field.errors = []
            raise StopValidation()

    def _is_empty(self, value: Any) -> bool:
        return isinstance(value, str) and not self.string_check(value)
