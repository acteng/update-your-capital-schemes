from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from govuk_frontend_wtf.wtforms_widgets import GovCheckboxInput, GovDateInput
from wtforms import DateField, Field
from wtforms.fields.numeric import IntegerField
from wtforms.form import BaseForm
from wtforms.validators import InputRequired, Optional, StopValidation


class CustomMessageIntegerField(IntegerField):
    """
    An integer field that allows the error message for invalid values to be customised.

    See: https://github.com/wtforms/wtforms/issues/832
    """

    def __init__(
        self,
        label: str | None = None,
        validators: tuple[Callable[[BaseForm, CustomMessageIntegerField], object], ...] | list[Any] | None = None,
        invalid_message: str = "Not a valid integer value.",
        **kwargs: Any,
    ):
        super().__init__(label, validators, **kwargs)
        self._invalid_message = invalid_message

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
            raise ValueError(self._invalid_message)


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
        invalid_message: str = "Not a valid date value.",
        **kwargs: Any,
    ):
        super().__init__(label, validators, format, **kwargs)
        self._invalid_message = invalid_message

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

        raise ValueError(self._invalid_message)


class FieldsetGovCheckboxInput(GovCheckboxInput):  # type: ignore
    """
    A GOV.UK checkbox input widget that omits an empty hint and supports adding a fieldset.

    See:
    - https://github.com/LandRegistry/govuk-frontend-wtf/issues/89
    - https://github.com/LandRegistry/govuk-frontend-wtf/pull/90
    """

    def map_gov_params(self, field: Field, **kwargs: Any) -> dict[str, Any]:
        params: dict[str, Any] = super().map_gov_params(field, **kwargs)

        if params.get("hint") == {"text": ""} and not field.description:
            del params["hint"]

        if "params" in kwargs:
            override_params: dict[str, Any] = kwargs["params"]
            if "fieldset" in override_params:
                params["fieldset"] = override_params["fieldset"]

        return params


class RemoveLeadingZerosGovDateInput(GovDateInput):  # type: ignore
    """
    A GOV.UK date input widget that removes leading zeros from day and month fields.

    See: https://github.com/LandRegistry/govuk-frontend-wtf/issues/85
    """

    def map_gov_params(self, field: Field, **kwargs: Any) -> dict[str, Any]:
        params: dict[str, Any] = super().map_gov_params(field, **kwargs)

        if field.raw_data is None and field.data:
            day, month = field.data.strftime("%-d %-m").split(" ")
            params["items"][0]["value"] = day
            params["items"][1]["value"] = month

        return params


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


class MultivalueInputRequired(InputRequired):
    """
    A validator that ensures input was provided and supports multivalued fields.

    See: https://github.com/wtforms/wtforms/issues/835
    """

    def __call__(self, form: BaseForm, field: Field) -> None:
        if field.raw_data and all(field.raw_data):
            return

        if self.message is None:
            message = field.gettext("This field is required.")
        else:
            message = self.message

        field.errors = []
        raise StopValidation(message)
