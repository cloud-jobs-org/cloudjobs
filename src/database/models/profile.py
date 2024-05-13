from pydantic import BaseModel, Field, Extra


class Profile(BaseModel):
    """
        **Profile**
            allows users to create personalized settings
            such us - deposit multiplier

    """
    uid: str
    main_game_id: str | None
    profile_name: str | None
    notes: str | None
    currency: str = Field(default="$")

    # class Config:
    #     extra = Extra.ignore

    def __eq__(self, other):
        if not isinstance(other, Profile):
            return False
        return self.main_game_id == other.main_game_id


class ProfileUpdate(BaseModel):
    uid: str
    main_game_id: str | None
    profile_name: str | None
    notes: str | None
    currency: str | None

    class Config:
        extra = Extra.ignore
