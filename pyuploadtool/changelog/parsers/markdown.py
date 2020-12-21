from .parser import ChangelogParser


class MarkdownChangelogParser(ChangelogParser):
    def render_to_markdown(self):
        """
        Get Markdown MarkdownChangelogParser
        :return:
        :rtype:
        """
        markdown_changelog = list()

        # add the title if it is provided
        if self.title is not None:
            markdown_changelog.append(f"# {self.title}")

        for spec in self.changelog.structure:

            if len(self.changelog[spec]) > 0:
                # append a new line before then next section
                markdown_changelog.append("\n")
                markdown_changelog.append(f"## {self.changelog.structure.get(spec)}")

            for commit in self.changelog[spec]:
                author_name = commit.get("author")
                commit_sha = commit.get("sha")
                message = commit.get("message")
                if self.commit_link_prefix:
                    author = f"([{author_name}]({self.commit_link_prefix}/{commit_sha}))"
                else:
                    author = f"({author_name})"

                markdown_changelog.append(f"* {message} {author}")

        return "\n".join(markdown_changelog)
