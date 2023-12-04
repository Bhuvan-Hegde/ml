import mysql.connector
from PyQt5 import QtCore, QtWidgets, uic
import datetime

class ParkingSystem(QtWidgets.QMainWindow):
    def __init__(self):
        super(ParkingSystem, self).__init__()
        uic.loadUi("front.ui", self)

        self.initialize_database()

        self.ENTRYBUTTON.released.connect(self.process_entry)
        self.EXITBUTTON.released.connect(self.process_exit)

    def initialize_database(self):
        self.mydb = mysql.connector.connect(host="localhost", user="smoke", passwd="hellomoto", database="car", autocommit=True)
        self.mycursor = self.mydb.cursor()

        # You may want to check if the tables already exist before creating them
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS slot(carNumber VARCHAR(15), slot int)")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS entry(carNumber VARCHAR(15), entry TIMESTAMP)")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS exits(carNumber VARCHAR(15), exit1 TIMESTAMP)")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS duration(carNumber VARCHAR(15), durationInSec int)")
        self.mycursor.execute("CREATE TABLE IF NOT EXISTS cost(carNumber VARCHAR(15), cost int)")

    def process_entry(self):
        car_number = self.lineEdit.text().strip()
        if not car_number:
            self.show_message("Invalid", "Car number cannot be empty.")
            return

        if self.check_duplicate(car_number):
            self.show_message("Duplicate", "Car number already exists in the parking.")
            return

        slot_number = self.get_available_slot()
        if slot_number is None:
            self.show_message("Error", "No available parking slots.")
            return

        entry_time = datetime.datetime.now()

        self.mycursor.execute("INSERT INTO slot (carNumber, slot) VALUES (%s, %s)", (car_number, slot_number))
        self.mycursor.execute("INSERT INTO entry (carNumber, entry) VALUES (%s, %s)", (car_number, entry_time))

        self.update_ui_after_entry(slot_number)

    def check_duplicate(self, car_number):
        self.mycursor.execute("SELECT carNumber FROM slot WHERE carNumber = %s", (car_number,))
        return bool(self.mycursor.fetchone())

    def get_available_slot(self):
        for slot_number, occupied in enumerate(slots, start=1):
            if not occupied:
                return slot_number
        return None

    def update_ui_after_entry(self, slot_number):
        slots[slot_number - 1] = True
        self.show_message("Entry Successful", f"Car parked in slot: {slot_number}")
        self.update_slot_ui()

    def update_slot_ui(self):
        for i, occupied in enumerate(slots):
            slot_button = getattr(self, f"s{i + 1}")
            color = "#FF0B00" if occupied else "#40FF50"
            slot_button.setStyleSheet(f"background-color: {color}")

    def process_exit(self):
        car_number = self.lineEdit.text().strip()
        if not car_number:
            self.show_message("Invalid", "Car number cannot be empty.")
            return

        exit_time = datetime.datetime.now()

        if not self.check_duplicate(car_number):
            self.show_message("Invalid Entry", "Car number does not exist in the parking.")
            return

        slot_number = self.get_slot_number(car_number)

        self.mycursor.execute("UPDATE exits SET exit1 = %s WHERE carNumber = %s", (exit_time, car_number))

        self.calculate_duration_and_cost(car_number, exit_time)

        self.update_ui_after_exit(slot_number)

    def get_slot_number(self, car_number):
        self.mycursor.execute("SELECT slot FROM slot WHERE carNumber = %s", (car_number,))
        return self.mycursor.fetchone()[0]

    def calculate_duration_and_cost(self, car_number, exit_time):
        self.mycursor.execute("SELECT entry FROM entry WHERE carNumber = %s", (car_number,))
        entry_time = self.mycursor.fetchone()[0]
        duration = int((exit_time - entry_time).total_seconds())

        cost = min(150, 10 * duration)

        self.mycursor.execute("UPDATE duration SET durationInSec = %s WHERE carNumber = %s", (duration, car_number))
        self.mycursor.execute("UPDATE cost SET cost = %s WHERE carNumber = %s", (cost, car_number))

        self.show_message("Exit Successful", f"Duration: {duration} seconds\nCost: Rs.{cost}")

    def update_ui_after_exit(self, slot_number):
        slots[slot_number - 1] = False
        self.update_slot_ui()

    def show_message(self, title, message):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

def main():
    app = QtWidgets.QApplication([])
    window = ParkingSystem()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
