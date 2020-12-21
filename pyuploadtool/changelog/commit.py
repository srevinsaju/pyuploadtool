from github.Commit import Commit

from .author import Author


class ChangelogCommit:
    def __init__(
        self,
        author: Author,
        message: str,
        sha: str,
    ):
        self._sha = sha
        self._author = author
        self.message = message

    def __repr__(self):
        return f"{self.__name__}"

    @property
    def author(self):
        return self._author

    @property
    def sha(self):
        return self._sha

    @classmethod
    def from_github_commit(cls, commit: Commit):
        author = Author(
            name=commit.author.name,
            email=commit.author.email
        )
        message = commit.commit.message
        sha = commit.sha
        return ChangelogCommit(
            author=author,
            message=message,
            sha=sha
        )
