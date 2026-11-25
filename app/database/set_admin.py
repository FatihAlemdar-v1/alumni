import argparse

from app.security import promote_admin


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote an existing user to administrator.")
    parser.add_argument("email", help="email address of the registered account")
    args = parser.parse_args()
    promote_admin(args.email)
    print(f"Administrator role granted to {args.email}.")


if __name__ == "__main__":
    main()
