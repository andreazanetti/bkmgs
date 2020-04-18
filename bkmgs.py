from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify
import json
import os.path
from werkzeug.utils import secure_filename
import os

import bkm_search as bks
import utilities.url_utils as ul

# os.environ["FLASK_ENV"] = "development" <-- Todo: check if this makes sense

app = Flask(__name__)
app.secret_key = '123123'
# there sould be a very random key here!!! used to communicate with the user
# - for message flashing to the user to work

@app.route('/') #jinjia templates
def home():
    bks.system_and_env_helper() # this requires a console answer from the user to check proxy settings!!!
    return render_template('home.html', codes=session.keys())
    # return object to be displayed,


@app.route('/your-url', methods=['GET', 'POST'])
def your_url():
    if request.method == 'POST':

        # dict with key short_code for link, value the actual corresponding url
        urls = dict()

        # check if the file exists
        cd = '/Users/azanetti/PycharmProjects/bkmgs'
        # os.getcwd() doing this gets the pycharm binary folder!!!!
        # as Flask server is run by Pycharm and the cwd is the bin dir!

        # check if my form has been used:
        if ('usercode' in request.form.keys()) | \
                ('bookmarks' in request.files.keys()) | \
                ("search_pattern" in request.form.keys()):
            print("GOT ONE OF THE CODES!")
            print(request.form['usercode'])
            print(request.form['search_pattern'])

            f = request.files['bookmarks']
            unique_name = request.form['usercode'] + '_' + secure_filename(f.filename)
            full_name = cd + '/static/users_uploads/' + unique_name
            f.save(full_name)

            # here I invoke the search part passing pattern and bookmarks file
            # then the results are displayed on the result page

            # Get user bookmarks into a manageable dict
            bmk_links = bks.get_Chrome_bookmarks_data(full_name)

            # and report on the bookmarks status, for now only to local ouput..
            # Todo: report this on the output webpage
            # bks.report_on_data(bmk_links)

            klist = list(bmk_links.link_dict.keys())
            # Todo: present the user to limit the scope of the search in his bookmars
            folder_list = [klist[i][3:] for i in range(50) if 'Science' in klist[i]]  # to test
            print(f"Your_url - Folder list is: {folder_list}")
            all_responses = list(ul.do_search(bmk_links,
                                         pattern_sought=request.form['search_pattern'],
                                         folder_list=folder_list))
            print("ALL Responses in your_url func is:", all_responses)
            if all_responses !=[]:
                return render_template('your_url.html',
                                   search_results=all_responses,
                                   search_pattern=request.form['search_pattern'])
            else:
                return render_template('your_url.html',
                                       search_results=['NOTHING FOUND :('],
                                       seach_pattern=request.form['search_pattern'])

        # this part below is relative to the link shortener service
        # which has been exlcuded in home.html
        # however Todo: I want to implement a tracking of searches and
        # cookie management similar to what follows
        filename = cd + '/' + 'urls.json'
        if os.path.exists(filename):
            print("loading data from existing file ", filename)
            with open(filename) as urls_file:
                urls = json.load(urls_file)

        # check the code if already in the dict
        if request.form['code'] in urls.keys():
            flash('Please pick a new shortname, it is already taken')
            return redirect(url_for('home'))

        # add input from the user to our dict and save it to json file
        if 'url' in request.form.keys():
            urls[request.form['code']] = {'url': request.form['url']}
        else:
            f = request.files['file']
            full_name = request.form['code'] + secure_filename(f.filename)
            f.save(cd + '/static/users_uploads/' + full_name)
            urls[request.form['code']] = {'file':full_name}

        # urls[request.form['code']] = {'url': request.form['url']}
        print("saving to file ", filename)
        with open(filename, 'w') as urls_file:
                json.dump(urls, urls_file)
                session[request.form['code']] = True  # cookie information update

        return render_template('your_url.html',
                                code=request.form['code'])
    else:
        return redirect(url_for('home'))#redirect('/')  # redirect to the home page


@app.route('/about')
def about():
    return 'This is about page'

# a variable route
@app.route('/<string:code>')
def redirect_to_url(code):  # code in these two lines are the same thing!
    url_file = '/Users/azanetti/PycharmProjects/bkmgs' + '/' + 'urls.json'
    if os.path.exists(url_file):
        with open(url_file) as urls_file:
            urls = json.load(urls_file)
            if code in urls.keys():
                if 'url' in urls[code].keys():
                    return redirect(urls[code]['url'])
                else:
                    return redirect(url_for('static', filename='users_uploads/' + urls[code]['file']))
    return abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route('/api')
def session_api():
    return jsonify(list(session.keys()))

if __name__ == '__main__':
    app.run()

