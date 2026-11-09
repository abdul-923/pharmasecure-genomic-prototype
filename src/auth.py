

import streamlit as st
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


def authenticate_user(username, password):
    """Verify researcher credentials."""

    users = st.secrets.get("users", {})

    for account, details in users.items():

        if username != details["username"]:
            continue

        ph = PasswordHasher()

        try:
            ph.verify(details["password_hash"], password)

            return {
                "username": username,
                "role": details["role"],
            }

        except VerifyMismatchError:
            return None

    return None
