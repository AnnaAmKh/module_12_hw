from collections import UserDict
from datetime import datetime, timedelta
import json

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Invalid phone number format")
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        return len(value) == 10 and value.isdigit()

class Birthday(Field):
    def __init__(self, value=None):
        if value and not self.validate_birthday(value):
            raise ValueError("Invalid birthday format")
        super().__init__(value)
    def set_value(self, value):
        if value and not self.validate_birthday(value):
            raise ValueError("Invalid birthday format")
        super().set_value(value)
    @staticmethod
    def validate_birthday(value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def days_to_birthday(self):
        if self.value:
            dob = datetime.strptime(self.value, '%Y-%m-%d')
            today = datetime.now()
            next_birthday = datetime(today.year, dob.month, dob.day)
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, dob.month, dob.day)
            return (next_birthday - today).days
        else:
            return None

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        new_phone = Phone(phone)
        if new_phone.value not in [p.value for p in self.phones]:
            self.phones.append(new_phone)
            print(f"Phone number {new_phone.value} has been added to the contact.")
        else:
            print("Phone number already exists for this contact.")

    def remove_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                self.phones.remove(ph)
                break

    def edit_phone(self, old_phone, new_phone):
        old_phone_obj = Phone(old_phone)
        new_phone_obj = Phone(new_phone)

        found = False
        for i, stored_phone in enumerate(self.phones):
            if stored_phone.value == old_phone_obj.value:
                found = True
                if new_phone_obj.value != old_phone_obj.value and new_phone_obj.value not in [p.value for p in self.phones]:
                    self.phones[i] = new_phone_obj
                    print(f"Phone number {old_phone_obj.value} has been updated to {new_phone_obj.value}.")
                else:
                    print("New phone number already exists for this contact or is the same as the old one.")
                break

        if not found:
            raise ValueError("Phone number not found for this contact.")

    def find_phone(self, value):
        for phone in self.phones:
            if value == phone.value:
                return phone

    def __str__(self):
        phone_list = '; '.join(str(phone) for phone in self.phones)
        return f"Contact name: {self.name.value}, phones: {phone_list}"

    def days_to_birthday(self):
        return self.birthday.days_to_birthday() if self.birthday else None

class AddressBook(UserDict):
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        if record.name.value not in self.data:
            self.data[record.name.value] = record
            print(f"Record for {record.name.value} has been added to the address book.")
        else:
            print(f"Record for {record.name.value} already exists in the address book.")

    def find(self, name):
        if name in self.data:
            print(f"Record for {name} found in the address book.")
            return self.data[name]
        else:
            print(f"Record for {name} not found in the address book.")
            return None

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            print(f"Record for {name} has been deleted from the address book.")
        else:
            print(f"Record for {name} not found in the address book.")
    def iterator(self, batch_size):
        keys = list(self.data.keys())
        for i in range(0, len(keys), batch_size):
            yield [self.data[key] for key in keys[i:i+batch_size]]

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.data, file, default=self.serialize_contact, indent=4)

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                self.data = json.load(file, object_hook=self.deserialize_contact)
        except FileNotFoundError:
            print("File not found or empty. Loading failed.")

    def serialize_contact(self, obj):
        if isinstance(obj, Field):
            return obj.value
        return obj.__dict__

    def deserialize_contact(self, obj):
        if 'name' in obj and 'phones' in obj and 'birthday' in obj:
            record = Record(obj['name'])
            record.phones = [Phone(phone) for phone in obj['phones']]
            record.birthday = Birthday(obj['birthday'])
            return record
        return obj

    def search_contacts(self, search_string):
        matching_contacts = []

        for contact in self.data.values():
            if (
                search_string in contact.name.value or
                any(search_string in phone.value for phone in contact.phones)
            ):
                matching_contacts.append(contact)

        return matching_contacts

#Перевірка
address_book = AddressBook()

record1 = Record("Anna Amelina", "1995-05-02")
record1.add_phone("1234567890")
record1.add_phone("9876543210")
address_book.add_record(record1)

record2 = Record("Jane Amelina", "1994-12-23")
record2.add_phone("1112223333")
address_book.add_record(record2)


address_book.save_to_file("Address.json")

try:
    with open("Address.json", "r") as file:
        file_content = file.read()
        print("Contents of the file:")
        print(file_content)
except FileNotFoundError:
    print("File not found")

new_address_book = AddressBook()
new_address_book.load_from_file("Address.json")


search_string = "Dima"
matching_contacts = new_address_book.search_contacts(search_string)
if matching_contacts:
    print(f"Matching contacts for '{search_string}':")
    for contact in matching_contacts:
        print(contact)
else:
    print(f"No found for '{search_string}'")

new_record = Record("Olha Nilson", "2000-12-11")
new_record.add_phone("9998887777")
new_address_book.add_record(new_record)

new_address_book.delete("Jane Amelina")


record_to_edit = new_address_book.find("Anna Amelina")
if record_to_edit:
    record_to_edit.edit_phone("1234567890", "5555555555")

new_address_book.save_to_file("Address_v1.json")
