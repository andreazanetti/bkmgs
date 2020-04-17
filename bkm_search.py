import argparse
import getpass
import utilities.url_utils as ul
import os
import json


def report_on_data(bmk_links):
    '''
    Outputs info on the Chrome bookmarks status, how many, how many duplicates
    :param bmk_links: dfs_chrome_bookmarks object
    :return: None
    '''
    # Todo: should this be a method of dfs_chrome_bookmarks obj?
    print("...data about bookmarks obtained.")
    print(f"Number of links found: {len(bmk_links.link_list)}")
    # test for uniquess of links in the Bookmarks
    n_unique_links = len(set(i[0] for i in bmk_links.link_list))
    n_links = len(bmk_links.link_list)
    if n_links != n_unique_links:
        print(f"{n_links - n_unique_links} Duplicate links exists in your bookmarks!")
    else:
        print("There are no duplicate links! OK!")
    ask = input("\nDo you want to print the obtained links out? Y/N/How many? ")
    if str(ask).strip(' ') == 'Y':
        myprint(bmk_links.link_list, N=n_links)
    elif (int(ask) > 0) and (int(ask) <= n_links):
        myprint(bmk_links.link_list, N=int(ask))
        # Todo: do this well taking care of the N case....

    return None


def system_and_env_helper():
    '''
    Collects info about the system, platform and check/set env variables
    :return: list of proxy related env variables name
    '''

    # check and set env variables, get environment
    env_keys = os.environ.keys()

    # collect env variables related to proxy settings
    print("\n\n\nCurrent environment status relevant to proxy configuration is the following:\n")
    proxy_env_keys = [k for k in
                      env_keys if ("PROXY" in k.upper()
                                   and "NO_PROXY" not in k.upper())]
    for k in proxy_env_keys:
        print(f"proxy related env variable {k} = {os.environ[k]}")

    # let the user choose about what proxy settings to use
    proxy_choice = input("\n\nDo you want to use these proxy settings (Y) or you want to skip the proxy (S)?")
    # Todo: check input for correctness
    if proxy_choice.upper() == 'S':
        for k in proxy_env_keys:
            del (os.environ[k])
        print("\nOK. Status of proxy environment variables has changed:\n")
        for k in proxy_env_keys:
            print(f'{k}={os.environ.get(k)}')

    return proxy_env_keys


def print_env():
    '''
    Helper function to print env variables
    :return: None
    '''
    for k, v in os.environ.items():
        print(f'{k}={v}')

    return None


def myprint(stack, N=1000, offset=3):
    '''
    Helper to print out a list of tuples with the second element being a list
    :param stack:  list of tuples
    :param N:      default max elements to print
    :param offset: exclude offset initial elements of the second component
    :return:       None
    '''
    i = 0
    while stack and i < N:
        k, v = stack.pop()
        print(i, ' ', k, v[offset:])  # exclude ('na', 'na', 'na',)
        i += 1


def get_Chrome_bookmarks_data(bmk_file):
    '''
    Open the Chrome bookmarks file of the user and
    return an object that contains all the links in a list of tuples
    :param bmk_file:
    :return: class dfs_chrome_bookmarks object with the list of tuples (folder, links) filled
    '''
    # Todo: make it return a dict with keys the location in the bookmark tree and values
    # Todo: the list of urls for each folder

    with open(bmk_file, 'rt') as data_file:
        bookmark_data = json.load(data_file)
    exx = ul.dfs_chrome_bookmarks(bookmark_data)
    return exx


def main(username, lpattern):
    '''
    Search for pattern in the list of Chrome bookmarks
    :param username: useful to find the Chrome Bookmarks
    :param lpattern: pattern to match in the bookmarked page content
    '''
    # print some info about the system and set environment according to user's preferences
    proxy_env_keys = system_and_env_helper()

    # identify bookmarks file
    # Todo: check for data in input to be ok and deal with non-Mac cases
    # Todo: also the user should be able to specify the full path
    bookmarks_file = username.join(['/Users/', '/Library/Application\ Support/Google/Chrome/Default/Bookmarks'])
    bookmarks_file = bookmarks_file.replace("\\", '')
    print(f"\nLooking into Bookmarks file: {bookmarks_file}")

    # Get bookmarks into a manageable dict
    bmk_links = get_Chrome_bookmarks_data(bookmarks_file)

    # and report on the bookmarks status
    report_on_data(bmk_links)

    # search for chosen pattern into a specified subset of bookmarked links
    # Todo: user should input the pattern here and not only on cli command,
    # Todo: and also the set of bookmarks folders to look into

    # quick test on searching to match a pattern on a subset of bookmarked links:
    folder_list = [('Bookmarks Bar', 'Andrea', 'Science', 'Ricerca'),
                       ('Bookmarks Bar', 'POL PHD', 'MathCognition')]

    all_responses = ul.do_search(bmk_links, pattern_sought=lpattern, folder_list=folder_list)

    print(f"main receives all these reponses: {list(all_responses)}")
    # check this: https://ahrefs.com/blog/google-advanced-search-operators/
    # and also https://github.com/daku/SearchMark


if __name__ == '__main__':
    # get username
    uname = getpass.getuser()

    # get script params
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pattern', help='string to match in the bookmarked pages')
    args = parser.parse_args()
    pattern = args.pattern

    # start
    main(uname, pattern)
