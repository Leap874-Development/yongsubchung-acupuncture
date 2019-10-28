# This file generates random entries in the database for testing purposes
from random import randint as rand, choice
import database
import datetime
import faker

db = database.Database('database.db')

try: db.doctor_add('admin', 'password')
except database.DoctorExists: pass

# {
#     'job': 'Purchasing manager',
#     'company': 'Rodriguez PLC',
#     'ssn': '588-05-3495',
#     'residence': '095 Miranda Glen\nWeissville, AR 62893',
#     'current_location': (Decimal('39.286206'), Decimal('-161.761068')),
#     'blood_group': 'AB+',
#     'website': ['http://www.macias.org/', 'https://www.wells.com/', 'https://buckley.com/', 'https://castillo.com/'],
#     'username': 'tonyramos',
#     'name': 'Ann Finley',
#     'sex': 'F',
#     'address': '006 Thomas Cliffs Apt. 383\nWhitefurt, UT 30098',
#     'mail': 'stephanie49@hotmail.com',
#     'birthdate': datetime.date(1955, 3, 16)
# }

allergies = ['Eggs', 'Peanuts', 'Soy', 'Gluten']

def random_phone():
	area_code = choice('123456789')
	last = choice('123456789')
	for _ in range(2):
		area_code += choice('0123456789')
	for _ in range(6):
		last += choice('0123456789')
	return area_code + last

N = 200
for _ in range(N):
	fake = faker.Faker()
	person = fake.profile()
	o = 0
	if len(person['name'].split()) > 2: o = 1
	fn = person['name'].split()[0 + o]
	ln = person['name'].split()[1 + o]
	print(_, fn, ln)
	a1 = person['residence'].split('\n')[0]
	a2 = person['residence'].split('\n')[1]
	hist = person['job'] + ' ' + person['blood_group']
	allergy = None
	attach = None
	f2 = None
	if rand(0, 100) < 50: allergy = choice(allergies)
	if rand(0, 100) < 70: attach = choice(person['website'])
	if rand(0, 100) < 25: f2 = random_phone()
	db.patient_add(
		ln, fn, person['sex'].lower(), person['birthdate'],
		height=rand(48, 78), weight=rand(90, 230), addr1=a1,
		addr2=a2, phone1=random_phone(), phone2=f2,
		email=person['mail'], medical_history=hist,
		medications=person['company'], allergy=allergy,
		note=' '.join(fake.sentences(nb=rand(1, 5))),
		attachment=attach
	)

# self, cur, last_name, first_name, gender, dob,
#                     height=None, weight=None, addr1=None, addr2=None,
#                     phone1=None, phone2=None, email=None, medical_history=None,
#                     medications=None, family_hx=None, allergy=None, note=None,
#                     attachment=None):

# db.patient_add(
#     'Jules', 'Mary', 'f', datetime.date(1956, 3, 14),
#     height=65, weight=196, addr1='5677 Autumn Drive',
#     email='mjuliee3@gmail.com', phone1=6699937412
# )



