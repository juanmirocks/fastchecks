from fastchecks.util import replace_url_last_segment


def test_replace_url_last_segment():
    fun = replace_url_last_segment
    new_segment = "fastchecks"

    test_cases = [
        # (url, expected_result)
        ("postgresql://localhost/postgres", "postgresql://localhost/fastchecks"),
        ("postgresql://localhost/postgres?sslmode=require", "postgresql://localhost/fastchecks?sslmode=require"),
        (
            "postgresql://username:password@localhost:5432/postgres?sslmode=require",
            "postgresql://username:password@localhost:5432/fastchecks?sslmode=require",
        ),
    ]

    for url, expected_result in test_cases:
        assert fun(url, new_segment) == expected_result
