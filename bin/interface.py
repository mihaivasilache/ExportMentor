from main import *
from Tkinter import *
import json
import db_util
import winmentor
import tkMessageBox
import datetime
CONFIG = json.load(open('./bin/config', 'r'))


class Winmentor_export(Frame):
    def validate(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD HH:MM:SS")

    def generate(self):
        start_date = self.start_date.get().strip()
        finish_date = self.finish_date.get().strip()
        try:
            self.validate(start_date)
            self.validate(finish_date)
            db = db_util.DbConnection(CONFIG['creds'])
            invoices = invoices_to_json(db, start_date, finish_date)
            db.close()

            mentor = winmentor.Winmentor()
            mentor.create_export_file_from_json(invoices)
            mentor.write_to_file()
            tkMessageBox.showinfo('Succes', 'Finished to generate log!')
        except Exception as e:
            print e
            tkMessageBox.showerror("Error", e.__str__())

    def createWidgets(self):
        Label(self, text="From Date").grid(row=0, column=0, columnspan=3)
        Label(self, text="To Date").grid(row=1, column=0, columnspan=3)

        self.start_date = Entry(self)
        self.finish_date = Entry(self)

        yesterday = datetime.datetime.today() - datetime.timedelta(1)

        self.start_date.insert(0, yesterday.strftime('%Y-%m-%d 00:00:00'))
        self.finish_date.insert(0, yesterday.strftime('%Y-%m-%d 23:59:59'))

        self.start_date.grid(row=0, column=3, columnspan=3)
        self.finish_date.grid(row=1, column=3, columnspan=3)

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit

        self.QUIT.grid(row=2, column=4)

        self.generate_export_files = Button(self)
        self.generate_export_files["text"] = "Generate",
        self.generate_export_files["command"] = self.generate

        self.generate_export_files.grid(row=2, column=1)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()


def main():
    root = Tk()
    root.title('Winexport')
    app = Winmentor_export(master=root)
    app.mainloop()
    root.destroy()


if __name__ == '__main__':
    main()
