import requests
import os
import subprocess


UPDATE_FILES = ["bin/coduri", "bin/db_util.py", "bin/interface.py", "bin/main.py", "bin/winmentor.py",
                "export_facturi.bat"]


def check_for_update(update_file_name, update_file=False):
    print "Requesting for", update_file_name
    response = requests.get("https://raw.githubusercontent.com/mihaivasilache/ExportMentor/master/%s"
                            % update_file_name)
    text_form_site = response.text
    text_from_file = open(os.path.join('../', update_file_name), 'r').read()
    if text_form_site != text_from_file:
        fd = open(os.path.join('../', update_file_name), 'w')
        fd.write(text_form_site)
        fd.close()
        if update_file is True:
            return True
        else:
            print "Modified", update_file_name
    else:
        if update_file is True:
            return False


def main():
    if check_for_update("bin/update.py", True):
        print "Modifing update..."
        subprocess.call("python bin/update.py", cwd='../')
        exit()
    for i in UPDATE_FILES:
        check_for_update(i)


if __name__ == "__main__":
    main()
