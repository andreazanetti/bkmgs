'''
Module contains functions/classes to get and organize the list of urls
from the bookmarked ones, and launch the search using all or part of the bookmarks
'''

import json
from utilities.bigGsearch import search
from urllib.error import HTTPError
import time

__all__ = [

    # Main class to represent bookmarks.
    'dfs_chrome_bookmarks',

    # Search function.
    'do_search',
]

class dfs_chrome_bookmarks():
    """
    Class that explores the Chrome Bookmarks file
    to return a list of tuples, with (link, location in bmk tree)
    Params:
    count: number of links found
    link_list: list of tuples (link,location in bmk tree)"
    link_dict: dictionary of path: [list of links at that path]
    Methods:
    _explore_bmk_file: to fill the list of links and the dictionary
    """
    # Todo: make this class iterable (Iteration protocol support)

    def __init__(self, dd, loc=('na',)):
        self.count = 0
        self.link_list = []
        self.link_dict = dict()
        self._explore_bmk_file(dd, loc=('na',))


    def _explore_bmk_file(self, dd, loc=('na',)):
        '''
        Fills the link_list with visiting recursively the tree of bookmarks
        keeping track of the folder structure, so as for the user to select
        which folder to include or exclude later
        params: dd - dictionary
        return: nothing - side effect to fill self.link_list with tuple(url, (location in bmks))
        '''

        # if the dictionary is about a url, add the url the list of urls, along with its position
        # in the tree of bookmarks
        if 'url' in dd.keys():
            self.link_list.append((dd['url'], loc + (dd['name'],)))

            # fill the simplified dictionary
            if tuple(loc) not in self.link_dict.keys():
                self.link_dict[tuple(loc)] = [dd['url']]
            else:
                self.link_dict[tuple(loc)].append(dd['url'])

            # increment the count of links
            self.count += 1
        else:
            # The received dict is related to a folder of bookmarks
            for i in dd.keys():
                if isinstance(dd[i], dict):
                    # let's explore into dict in any case: we will select interesting info as we go deep
                    if 'name' in dd.keys():
                        ml = loc + (dd['name'],)
                    else:
                        ml = loc + ('na',)
                    # recursively look into subtree
                    self._explore_bmk_file(dd[i], ml)

                elif isinstance(dd[i], list):  # this is the case of the children list of dicts
                    for k in dd[i]:
                        if isinstance(k, dict):
                            if 'name' in dd.keys():
                                ml = loc + (dd['name'],)
                            else:
                                ml = loc + ('na',)
                            # recursively look into subtree, for each dict in the list of dicts
                            self._explore_bmk_file(k, ml)
                else:
                    pass
                    # Todo: Make sure this is never relevant case

        return None

# Todo: not used - check if this will be needed
def myprint_for_dict(dict_of_list_of_links, N=1000, offset=3):
    '''
    Helper to print out a list of tuples with the second element being a list
    :param dict_of_list_of_links:  dictionary of list of links, pertaining to a bookmark folder
    :param N:      default max elements to print
    :param offset: exclude offset initial elements of the second component
    :return:       None
    '''
    # Todo: make this check better
    assert(isinstance(dict_of_list_of_links, dict))

    for i, t in enumerate(dict_of_list_of_links.items()):
        (k, list_of_links) = t
        print(i,' ', k[offset:], list_of_links)


def _get_full_key(list_of_tuples, given_uncomplete):
    '''
    Getting the firt keys in list_of_lists_of_tuples that includes given_uncomplete
    :param list_of_tuples:
    :param given_uncomplete:
    :return: first matching key
    '''
    for ll in list_of_tuples:
            if ll[3:] == given_uncomplete:
                return ll[:]
    return None


def do_search(bmk_obj, pattern_sought=None, folder_list=None):
    '''
    Does the actual search for the pattern_sought in the urls contained in the
    bookmarks folder listed in the folder_list, using google.
    :param bmk_obj: dfs_chrome_bookmarks object representing the Chrome Bookmarks
    :param pattern_sought: pattern to match
    :param folder_list: list of Chrome Bookmarks folders for the specific search
    :return: all_responses: list of all links that match/contain the pattern
    '''
    # Using google to search on for pattern on selected bookmarks
    print(f"\n\n\ndo_search: Test of search of '{pattern_sought}' in selected bookmarks folders:\n{folder_list}")

    all_responses = []
    for i in folder_list:
        kk = _get_full_key(bmk_obj.link_dict.keys(), i)
        print(kk)

        # Todo: instead of looping over the list of links, pack a single request
        # with multiple domains (or pages) to look into it
        try:
            res = search(f"{pattern_sought}", domains=bmk_obj.link_dict[kk], stop=10)
            res = list(res)
            print(f"do_search receives this response: {res}")
            all_responses.extend(res)
            print(f"Status of all responses is:\n{all_responses}")
            time.sleep(5)  # avoid being banned by Google
            # Todo: Get from search the link with a sample of the sentence where the pattern was found
        except HTTPError as e:
                print(f"While analysing sites {bmk_obj.link_dict[kk]}\n got HTTP Error")
                print(f"HTTP Error: {e}")

    return all_responses