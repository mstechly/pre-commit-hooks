import pytest

from add_msg_issue_hook import add_msg_issue

TEMPLATE: str = "{subject}\n\n[{issue_id}]\n{body}"


class TestGetIssueIDSFromBranch:
    @staticmethod
    @pytest.mark.parametrize(
        "branch_name, issue_ids",
        [
            ("feature/TEAMID-010/something", ["TEAMID-010"]),
            ("feature/something/TEAMID-010", ["TEAMID-010"]),
        ],
    )
    def test_finds_existing_id(branch_name, issue_ids):
        assert add_msg_issue._get_issue_ids_from_branch_name(branch_name) == issue_ids

    @staticmethod
    @pytest.mark.parametrize(
        "branch_name", ["main", "dev", "feature/bmummery/confetti"]
    )
    def test_ignores_nonexistant_ids(branch_name):
        assert add_msg_issue._get_issue_ids_from_branch_name(branch_name) == []


class TestIssueIsInMessage:
    @staticmethod
    @pytest.mark.parametrize(
        "issue_id, message", [("TESTID-010", "fix: TESTID-010: summary")]
    )
    def test_returns_true_if_issue_in_message(issue_id, message):
        assert add_msg_issue._issue_is_in_message(issue_id, message)

    @staticmethod
    @pytest.mark.parametrize(
        "issue_id, message", [("TESTID-010", "fix: TESTID-011: summary")]
    )
    def test_returns_false_if_issue_not_in_message(issue_id, message):
        assert not add_msg_issue._issue_is_in_message(issue_id, message)

    @staticmethod
    @pytest.mark.parametrize(
        "issue_id, message", [("TESTID-010", "# fix: TESTID-010: summary")]
    )
    def test_returns_false_if_issue_only_in_comments(issue_id, message):
        assert not add_msg_issue._issue_is_in_message(issue_id, message)


@pytest.mark.parametrize(
    "message_in, message_out",
    [
        # Single text line
        (("Subject line."), ("Subject line.\n\n[{issue_id}]")),
        # 2 text lines, no linebreak
        (
            ("Subject line.\nBody line 1"),
            ("Subject line.\n\n[{issue_id}]\nBody line 1"),
        ),
        # 2 text lines, with linebreak
        (
            ("Subject line.\n\nBody line 1"),
            ("Subject line.\n\n[{issue_id}]\nBody line 1"),
        ),
        # Subject line and longer body
        (
            ("Subject line.\n\nBody line 1\nBody line 2"),
            ("Subject line.\n\n[{issue_id}]\nBody line 1\nBody line 2"),
        ),
        # Subject line and longer body with comments
        (
            (
                "Subject line.\n"
                "\n"
                "Body line 1\n"
                "# Comment line 1\n"
                "Body line 2\n"
                "# comment line 2"
            ),
            (
                "Subject line.\n"
                "\n"
                "[{issue_id}]\n"
                "Body line 1\n"
                "# Comment line 1\n"
                "Body line 2\n"
                "# comment line 2"
            ),
        ),
        # Single comment line
        (("# some comment"), ("[{issue_id}]\n# some comment")),
        (
            ("# some comment \n\n# some other comment\n# A third comment."),
            (
                "[{issue_id}]\n"
                "# some comment \n"
                "\n"
                "# some other comment\n"
                "# A third comment."
            ),
        ),
        # Body starting with comment
        (("Summary\n# some comment"), ("Summary\n\n[{issue_id}]\n\n# some comment")),
    ],
)
class TestInsertIssueIntoMessage:
    @staticmethod
    @pytest.mark.parametrize("issue_id", ["TESTID-12345"])
    def test_with_issue_id(message_in, message_out, issue_id):

        outstr = add_msg_issue._insert_issue_into_message(
            issue_id, message_in, TEMPLATE
        )

        expected_message_out = message_out.format(issue_id=issue_id)
        assert outstr == expected_message_out, (
            "insert_issue_into_message returned an incorrect string.\n"
            "Input string:\n" + "-" * 40 + "\n"
            f"{message_in}\n" + "-" * 40 + "\n"
            "Output string:\n" + "-" * 40 + "\n"
            f"{outstr}\n" + "-" * 40 + "\n"
            "Expected output:\n" + "-" * 40 + "\n"
            f"{expected_message_out}\n" + "-" * 40 + "\n"
        )
