from __future__ import annotations

import pytest
from werkzeug.datastructures import MultiDict
from wtforms.form import Form

from schemes.views.fields import CustomMessageIntegerField


class TestCustomMessageIntegerField:
    @pytest.fixture(name="form")
    def form_fixture(self) -> FakeForm:
        return FakeForm()

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


class FakeForm(Form):
    field = CustomMessageIntegerField()
    custom_message_field = CustomMessageIntegerField(message="My custom message")
