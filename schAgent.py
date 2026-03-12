import argparse
import getpass
from suds.client import Client
import sys
import ssl

def main(url, username, password, input_file):
    # Read and count reports from input file
    try:
        with open(input_file, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        count = len(lines)
    except FileNotFoundError:
        print(f"Input file '{input_file}' not found.")
        return
    print("Total reports:", count)

    # Connect to SOAP API and execute reports
    client = None
    session_id = None
    try:
        client = Client(url)
        session_id = client.service['SAWSessionService'].logon(username, password)
        print(f"Logged in. Session ID: {session_id}")

        for report in lines:
            print(f"Executing report: {report}")
            client.service['IBotService'].executeIBotNow(report, session_id)

    except ssl.SSLError as ssl_err:
        print("SSL certificate verification failed.")
        print("On macOS, please run:")
        print("/Applications/Python\\ 3.x/Install\\ Certificates.command")
        print("Replace '3.x' with your Python version.")
        print(f"Details: {ssl_err}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if session_id and client:
            try:
                client.service['SAWSessionService'].logoff(session_id)
                print("Logged off")
            except Exception as e:
                print(f"Error during logoff: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute Oracle Analytics IBots via SOAP API.")
    parser.add_argument("--url", required=True, help="SOAP API WSDL URL")
    parser.add_argument("--username", required=True, help="Username for authentication")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--password", help="Password for authentication")
    group.add_argument("--password-file", help="Path to a file containing the password")
    parser.add_argument("--input-file", default="input.txt", help="Path to input file with report names")
    args = parser.parse_args()

    password = args.password
    if args.password_file:
        try:
            with open(args.password_file, "r") as pf:
                password = pf.readline().strip()
        except Exception as e:
            print(f"Could not read password from file: {e}")
            sys.exit(1)
    if not password:
        password = getpass.getpass("Enter your password: ")
    main(args.url, args.username, password, args.input_file)


