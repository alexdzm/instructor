from itertools import product
from collections.abc import Iterable
from pydantic import BaseModel
import pytest
import instructor
from writerai import Writer
from instructor.dsl.partial import Partial

from .util import models, modes


class UserExtract(BaseModel):
    first_name: str
    age: int


@pytest.mark.parametrize("model, mode, stream", product(models, modes, [True, False]))
def test_writer_iterable_model(model: str, mode: instructor.Mode, stream: bool):
    client = instructor.from_writer(client=Writer(), mode=mode)
    response = client.chat.completions.create(
        model=model,
        response_model=Iterable[UserExtract],
        max_retries=2,
        stream=stream,
        messages=[
            {"role": "user", "content": "Make two up people"},
        ],
    )
    for m in response:
        assert isinstance(m, UserExtract)


@pytest.mark.parametrize("model,mode", product(models, modes))
def test_writer_partial_model(model: str, mode: instructor.Mode):
    client = instructor.from_writer(client=Writer(), mode=mode)
    response = client.chat.completions.create(
        model=model,
        response_model=Partial[UserExtract],
        max_retries=2,
        stream=True,
        messages=[
            {"role": "user", "content": "{{ name }} is {{ age }} years old"},
        ],
        context={"name": "Jason", "age": 12},
    )
    final_model = None
    for m in response:
        assert isinstance(m, UserExtract)
        final_model = m

    assert final_model.age == 12
    assert final_model.first_name == "Jason"