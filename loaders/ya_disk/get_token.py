import argparse
import json
import sys
import yadisk

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--client_id",
        required=True,
        help="ClientID")

    parser.add_argument(
        "-s", "--secret",
        required=True,
        help="Client Secret")

    parser.add_argument(
        "-o", "--code",
        required=True,
        help="Code from URL")

    args = parser.parse_args()

    y = yadisk.YaDisk(args.client_id, args.secret)
    try:
        response = y.get_token(args.code)
    except yadisk.exceptions.BadRequestError:
        print("Wrong code")
        sys.exit(1)

    y.token = response.access_token

    if y.check_token():
        print("Sucessfully received token!")
        token_data = {"token" : y.token}
        with open("token.json", 'w') as f:
            f.write(json.dumps(token_data))
    else:
        print("Something went wrong. Not sure how though...")

if __name__ == "__main__":
    main()

