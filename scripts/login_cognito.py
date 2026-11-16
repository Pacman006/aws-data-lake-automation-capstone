#!/usr/bin/env python3
"""Interactive Cognito login. Prints access token only on request; never saves it."""
import argparse
import getpass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-id", required=True, help="CognitoClientId output")
    parser.add_argument("--region", default="ap-south-1")
    parser.add_argument("--profile")
    parser.add_argument("--show-token", action="store_true", help="Display sensitive token on your terminal")
    args = parser.parse_args()
    import boto3

    username = input("Cognito email: ").strip()
    password = getpass.getpass("Password (hidden): ")
    client = boto3.Session(profile_name=args.profile, region_name=args.region).client("cognito-idp")
    auth = client.initiate_auth(
        ClientId=args.client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
    )
    if "AuthenticationResult" not in auth:
        print("Additional challenge required:", auth.get("ChallengeName", "unknown"))
        return 1
    print("Authentication succeeded. Token expires in", auth["AuthenticationResult"]["ExpiresIn"], "seconds")
    if args.show_token:
        print(auth["AuthenticationResult"]["AccessToken"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
