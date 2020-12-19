
import os


# order them by priority
# https://cheatography.com/albelop/cheat-sheets/conventional-commits/
CONVENTIONAL_COMMIT_SPEC = {
    "feat":     "Features",
    "fix":      "Bug Fixes",
    "perf":     "Performance Improvements",
    "docs":     "Documentation",
    "ci":       "Continuous Integration",
    "refactor": "Refactoring",
    "test":     "Tests",
    "build":    "Builds",
    "revert":   "Reverts",
    "chore":    "Chores",
    "others":   "Commits"
}


class Changelog:
    def __init__(self, title=os.getenv("CHANGELOG_TITLE"), commit_link_prefix=None):
        """
        Generates a changelog by arranging the commits according
        to the Conventional Commit Spec

        :param title: the title of the release, generally, the tag name
        :type title: str

        :param commit_link_prefix: a link prefix, which can be used to show a commit
        for example
        commit_link_prefix = https://github.com/$GITHUB_REPOSITORY/commit
        here, we will add the commit hash to the end.
        :type commit_link_prefix: str
        """

        # remove the trailing hash
        self.commit_link_prefix = commit_link_prefix.rstrip("/")
        self.title = title

        self._data = dict()

        for spec in CONVENTIONAL_COMMIT_SPEC:
            self._data[spec] = list()

    def push(self, commit: dict):
        """
        Adds a commit to the changelog and aligns each commit
        based on their category. See CONVENTIONAL_COMMIT_SPEC
        :return: The classification of the commit == CONVENTIONAL_COMMIT_SPEC.keys()
        :rtype: str
        """
        message = commit.pop("message")
        for spec in CONVENTIONAL_COMMIT_SPEC:
            if message.startswith(f"{spec}:"):
                self._data[spec].append({
                    "message": message[len(f"{spec}:") + 1:].strip(),
                    **commit
                })
                return spec
            elif message.startswith(f"{spec} "):
                self._data[spec].append({
                    "message": message[len(f"{spec}") + 1:].strip(),
                    **commit
                })
                return spec

        # it did not fit into any proper category, lets push to others
        self._data["others"].append({
            "message": message.strip(),
            **commit
        })
        return "others"

    def get_changelog(self):
        """
        Returns the stored changelog metadata
        :return:
        :rtype:
        """
        return self._data

    def render_to_markdown(self):
        """
        Get Markdown Changelog
        :return:
        :rtype:
        """
        markdown_changelog = list()

        # add the title if it is provided
        if self.title is not None:
            markdown_changelog.append(f"# {self.title}")

        for spec in self._data:

            if len(self._data[spec]) > 0:
                # append a new line before then next section
                markdown_changelog.append("\n")
                markdown_changelog.append(f"## {CONVENTIONAL_COMMIT_SPEC.get(spec)}")

            for commit in self._data[spec]:
                author_name = commit.get("author")
                commit_sha = commit.get("sha")
                message = commit.get("message")
                if self.commit_link_prefix:
                    author = f"([{author_name}]({self.commit_link_prefix}/{commit_sha}))"
                else:
                    author = f"({author_name})"

                markdown_changelog.append(f"* {message} {author}")

        return '\n'.join(markdown_changelog)
