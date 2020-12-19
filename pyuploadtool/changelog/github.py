import os
import requests

from .changelog import Changelog
from ..logging import make_logger


class GitHubChangelogGenerator:
    logger = make_logger("github-changelog-generator")

    def __init__(self, metadata, github_token):
        """
        Prepares the changelog using GitHub REST API by
        comparing the current commit against the latest release (pre-release / stable)

        :param metadata:
        :type metadata: ReleaseMetadata
        :param github_token: A GitHub Personal Access Token to handle GitHub API calls
        :type github_token: str
        """
        self._metadata = metadata

        self.github_token = github_token
        self.github_repository = metadata.repository_slug
        self.commit_sha = metadata.commit
        self.headers = {
            "Authorization": f"token {self.github_token}"
        }

    def _get_github_api_repos(self, arg):
        """
        Helper function to aid github api calls.

        :param arg: https://docs.github.com/en/free-pro-team@latest/rest/reference/repos
        :type arg: str
        :return: JSON response
        :rtype: dict
        """
        api_endpoint = f"https://api.github.com/repos/{self.github_repository}/{arg}"
        self.logger.debug(f"Calling {api_endpoint}")
        raw_response = requests.get(api_endpoint, headers=self.headers)
        json_response = raw_response.json()
        return json_response

    def get_releases(self):
        """
        Get the json data of all releases

        :return: JSON data from GitHub API
        :rtype: dict
        """
        return self._get_github_api_repos("releases")

    def get_latest_release(self):
        """
        Gets the latest release by semver, like v8.0.1, v4.5.9, if not
        Fallback to continuous releases, like 'continuous', 'stable', 'nightly'

        :return: the tag name of the latest release, and the date on which it was created
        :rtype: dict
        """
        def get_release_metadata(r):
            """
            Return metadata containing
            * tag: name of the tag
            * created: when the tag was created

            :rtype: dict
            """
            return {
                "tag": r.get("tag_name"),
                "created": r.get("created_at")
            }

        releases = self.get_releases()
        _latest_release = None
        _rolling_release = None
        for release in releases:
            if not release.get("tag_name").startswith("v") or \
                    not release.get("tag_name")[0].isdigit():
                # the release does not follow semver specs

                if _rolling_release is None or (
                        _rolling_release and release.get("created_at") > _rolling_release.get("created")):
                    # probably, we are looking at a rolling release
                    # like 'continuous', 'beta', etc..
                    _rolling_release = get_release_metadata(release)

            elif _latest_release is None:
                # we still dont have a latest release,
                # so we need to set whatever release we currently are at
                # as the latest release
                _latest_release = get_release_metadata(release)

            elif release.get("created_at") > _latest_release.get("created"):
                # we found a release for which, the current release is newer
                # than the stored one
                _latest_release = get_release_metadata(release)

        # we found a release which does not follow
        # semver specs, and it is a probably a rolling release
        # just provide that as the latest release
        # so we need to return that, if we didnt find a suitable _latest_release
        return _latest_release or _rolling_release

    def get_commits_since(self, tag):
        """
        Gets all the commits since a tag to self.commit_sha
        :return
        """
        compare_json = self._get_github_api_repos(f"compare/{tag}...{self.commit_sha}")
        commits = compare_json.get("commits")

        # _refined commits are a list of commits in list of dictionary type
        # which contains the following data
        # ("sha", "author", "message")
        _refined_commits = list()

        for commit in commits:
            _refined_commits.append({
                "sha": commit.get("sha"),
                "author": commit.get("commit").get("author").get("name"),
                "message": commit.get("commit").get("message").split("\n")[0]
            })
        return _refined_commits

    def get_changelog(self):
        """
        Wrapper command to generate the changelog
        :return: markdown data as changelog
        :rtype: str
        """

        latest_release = self.get_latest_release()

        if latest_release is None:
            # We couldn't find out the latest release. Lets stick with
            # the commit above the commit we are working against.

            # FIXME: Looks like it works fine... Need some tests here
            latest_release = f"{self.commit_sha}^1"
        else:
            latest_release = latest_release.get("tag")

        commits = self.get_commits_since(latest_release)
        self.logger.debug(f"Found {len(commits)} commits")

        # generate a changelog
        chglog = Changelog(
            title=os.getenv("CHANGELOG_TITLE") or f"{self._metadata.tag}",
            commit_link_prefix="https://github.com/{self.github_repository}/commits")

        for commit in commits:
            chglog.push(commit)

        return chglog.get_changelog()
