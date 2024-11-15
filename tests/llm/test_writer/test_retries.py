from typing import Annotated
from pydantic import AfterValidator, BaseModel, Field
import pytest
import instructor
from itertools import product
from writerai import Writer
from .util import models, modes


def uppercase_validator(v):
    if v.islower():
        raise ValueError("Name must be in uppercase")
    return v


class UserDetail(BaseModel):
    first_name: Annotated[str, AfterValidator(uppercase_validator)] = Field(
        ..., description="The name of the user"
    )
    age: int


@pytest.mark.parametrize("model, mode", product(models, modes))
def test_upper_case(model: str, mode: instructor.Mode):
    client = instructor.from_writer(client=Writer(), mode=mode)
    response = client.chat.completions.create(
        model=model,
        response_model=UserDetail,
        messages=[
            {"role": "user", "content": "Extract `jason is 12`"},
        ],
        max_retries=3,
    )
    assert response.name == "JASON"


@pytest.mark.parametrize("model, mode", product(models, modes))
def test_upper_case_tenacity(model: str, mode: instructor.Mode):
    client = instructor.from_writer(client=Writer(), mode=mode)
    from tenacity import Retrying, stop_after_attempt, wait_fixed

    retries = Retrying(
        stop=stop_after_attempt(2),
        wait=wait_fixed(1),
    )

    response = client.chat.completions.create(
        model=model,
        response_model=UserDetail,
        messages=[
            {"role": "user", "content": "Extract `jason is 12`"},
        ],
        max_retries=retries,
    )
    assert response.name == "JASON"