from yoyo import step


__transactional__ = False


steps = [
    step(
        "CREATE DATABASE feast",
        "DROP DATABASE IF EXISTS feast"
    )
]