from yoyo import step


__transactional__ = False


steps = [
    step(
        "CREATE DATABASE mlflow",
        "DROP DATABASE IF EXISTS mlflow"
    )
]