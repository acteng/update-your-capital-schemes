from __future__ import annotations

from datetime import date, datetime

import pytest
from werkzeug.datastructures import MultiDict
from wtforms.form import Form
from wtforms.validators import StopValidation

from schemes.views.forms import (
    CustomMessageDateField,
    CustomMessageIntegerField,
    MultivalueInputRequired,
    MultivalueOptional,
    RemoveLeadingZerosGovDateInput,
)


@pytest.fixture(name="form")
def form_fixture() -> FakeForm:
    return FakeForm()


class TestCustomMessageIntegerField:
    def test_process_data_with_no_value(self, form: FakeForm) -> None:
        form.process(data={})

        assert form.field.data is None
        assert form.field.process_errors == []

    def test_process_data_with_integer(self, form: FakeForm) -> None:
        form.process(data={"field": "123"})

        assert form.field.data == 123
        assert form.field.process_errors == []

    def test_cannot_process_data_with_invalid_value(self, form: FakeForm) -> None:
        form.process(data={"field": "abc"})

        assert form.field.data is None
        assert form.field.process_errors == ["Not a valid integer value."]

    def test_cannot_process_data_with_invalid_value_uses_custom_message(self, form: FakeForm) -> None:
        form.process(data={"custom_message_field": "abc"})

        assert form.custom_message_field.data is None
        assert form.custom_message_field.process_errors == ["My custom message"]

    def test_process_formdata_with_no_value(self, form: FakeForm) -> None:
        form.process(formdata=MultiDict())

        assert form.field.data is None
        assert form.field.process_errors == []

    def test_process_formdata_with_integer(self, form: FakeForm) -> None:
        form.process(formdata=MultiDict([("field", "123")]))

        assert form.field.data == 123
        assert form.field.process_errors == []

    def test_cannot_process_formdata_with_invalid_value(self, form: FakeForm) -> None:
        form.process(formdata=MultiDict([("field", "abc")]))

        assert form.field.data is None
        assert form.field.process_errors == ["Not a valid integer value."]

    def test_cannot_process_formdata_with_invalid_value_uses_custom_message(self, form: FakeForm) -> None:
        form.process(formdata=MultiDict([("custom_message_field", "abc")]))

        assert form.custom_message_field.data is None
        assert form.custom_message_field.process_errors == ["My custom message"]


class TestCustomMessageDateField:
    def test_process_formdata_with_no_value(self, form: FakeForm) -> None:
        form.process(formdata=MultiDict())

        assert form.date_field.data is None
        assert form.date_field.process_errors == []

    def test_process_formdata_with_date(self, form: FakeForm) -> None:
        form.process(formdata=MultiDict([("date_field", "2000-01-01")]))

        assert form.date_field.data == date(2000, 1, 1)
        assert form.date_field.process_errors == []

    def test_cannot_process_formdata_with_invalid_value(self, form: FakeForm) -> None:
        form.process(formdata=MultiDict([("date_field", "2000-01-one")]))

        assert form.date_field.data is None
        assert form.date_field.process_errors == ["Not a valid date value."]

    def test_cannot_process_formdata_with_invalid_date_uses_custom_message(self, form: FakeForm) -> None:
        form.process(formdata=MultiDict([("custom_message_date_field", "2000-01-one")]))

        assert form.custom_message_date_field.data is None
        assert form.custom_message_date_field.process_errors == ["My custom message"]


class TestRemoveLeadingZerosGovDateInput:
    def test_date_values_when_missing(self, form: FakeForm) -> None:
        widget = RemoveLeadingZerosGovDateInput()

        params = widget.map_gov_params(form.date_field, id="date_field")

        assert [item["value"] for item in params["items"]] == [None, None, None]

    def test_date_values_have_no_leading_zeros(self, form: FakeForm) -> None:
        form.date_field.data = datetime(2000, 1, 2)
        widget = RemoveLeadingZerosGovDateInput()

        params = widget.map_gov_params(form.date_field, id="date_field")

        assert [item["value"] for item in params["items"]] == ["2", "1", "2000"]

    def test_date_values_when_raw_data(self, form: FakeForm) -> None:
        form.date_field.data = datetime(2000, 1, 2)
        form.date_field.raw_data = ["02", "01", "2000"]
        widget = RemoveLeadingZerosGovDateInput()

        params = widget.map_gov_params(form.date_field, id="date_field")

        assert [item["value"] for item in params["items"]] == ["02", "01", "2000"]


class TestMultivalueOptional:
    @pytest.mark.parametrize(
        "raw_data",
        [
            ["x"],
            ["x", "y"],
            ["", "y"],
            [" ", "y"],
            ["x", ""],
            ["x", " "],
        ],
    )
    def test_continue_when_at_least_one_value_present(self, form: FakeForm, raw_data: list[str]) -> None:
        multivalue_optional = MultivalueOptional()
        form.field.errors = ["error"]
        form.field.raw_data = raw_data

        multivalue_optional(form, form.field)

        assert form.field.errors == ["error"]

    @pytest.mark.parametrize(
        "raw_data",
        [
            [],
            [""],
            [" "],
            ["", ""],
            [" ", " "],
        ],
    )
    def test_stop_when_all_values_empty(self, form: FakeForm, raw_data: list[str]) -> None:
        multivalue_optional = MultivalueOptional()
        form.field.errors = ["error"]
        form.field.raw_data = raw_data

        with pytest.raises(StopValidation):
            multivalue_optional(form, form.field)

        assert not form.field.errors


class TestMultivalueInputRequired:
    @pytest.mark.parametrize(
        "raw_data",
        [
            ["x"],
            ["x", "y"],
        ],
    )
    def test_continue_when_all_values_present(self, form: FakeForm, raw_data: list[str]) -> None:
        multivalue_input_required = MultivalueInputRequired()
        form.field.errors = ["error"]
        form.field.raw_data = raw_data

        multivalue_input_required(form, form.field)

        assert form.field.errors == ["error"]

    @pytest.mark.parametrize(
        "raw_data",
        [
            [],
            [""],
            ["", "y"],
            ["x", ""],
        ],
    )
    def test_stop_when_at_least_one_value_empty(self, form: FakeForm, raw_data: list[str]) -> None:
        multivalue_input_required = MultivalueInputRequired()
        form.field.errors = ["error"]
        form.field.raw_data = raw_data

        with pytest.raises(StopValidation, match="This field is required."):
            multivalue_input_required(form, form.field)

        assert not form.field.errors

    def test_stop_when_at_least_one_value_empty_with_custom_message(self, form: FakeForm) -> None:
        multivalue_input_required = MultivalueInputRequired(message="Enter a field")
        form.field.raw_data = ["x", ""]

        with pytest.raises(StopValidation, match="Enter a field"):
            multivalue_input_required(form, form.field)


class FakeForm(Form):
    field = CustomMessageIntegerField()
    custom_message_field = CustomMessageIntegerField(invalid_message="My custom message")
    date_field = CustomMessageDateField()
    custom_message_date_field = CustomMessageDateField(invalid_message="My custom message")
