from dataclasses import dataclass

from sixchan.models import UserAccount, UserProfile


@dataclass
class UserQueryModel:
    username: str
    display_name: str
    introduction: str


def get_user(username: str) -> UserQueryModel:
    query = (
        UserAccount.query.filter_by(username=username)
        .with_entities(
            UserAccount.username,
            UserProfile.display_name,
            UserProfile.introduction,
        )
        .join(UserProfile)
    )
    return UserQueryModel(**query.first())
